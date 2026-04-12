import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Repository, Digest
from app.services.github_service import github_service
from app.services.email_service import email_service
from app.agents.digest_agent import run_digest_agent

router = APIRouter(prefix="/digests", tags=["digests"])


class DigestRequest(BaseModel):
    repo_id: int
    period_days: int = 7
    send_email: bool = True


class DigestOut(BaseModel):
    id: int
    repository_id: int
    period_days: int
    summary: str
    highlights: list[str]
    action_items: list[str]
    overall_health: str
    health_reason: str
    email_sent: bool
    created_at: str

    class Config:
        from_attributes = True


def _parse_json_field(value: str | None) -> list:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return [value]


@router.get("/", response_model=list[DigestOut])
def list_digests(repo_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Digest)
    if repo_id:
        q = q.filter_by(repository_id=repo_id)
    digests = q.order_by(Digest.created_at.desc()).limit(50).all()

    result = []
    for d in digests:
        raw = json.loads(d.raw_stats or "{}")
        result.append(DigestOut(
            id=d.id,
            repository_id=d.repository_id,
            period_days=d.period_days,
            summary=d.summary,
            highlights=_parse_json_field(d.highlights),
            action_items=_parse_json_field(d.action_items),
            overall_health=raw.get("overall_health", "yellow"),
            health_reason=raw.get("health_reason", ""),
            email_sent=d.email_sent,
            created_at=d.created_at.isoformat(),
        ))
    return result


@router.post("/generate")
def generate_digest(
    payload: DigestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    repo = db.query(Repository).filter_by(id=payload.repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Fetch GitHub activity
    try:
        activity = github_service.fetch_activity(
            repo.owner, repo.name, payload.period_days
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Run LangGraph agent
    digest_data = run_digest_agent(activity)

    # Persist digest
    import dataclasses
    activity_dict = dataclasses.asdict(activity)

    digest = Digest(
        repository_id=repo.id,
        period_days=payload.period_days,
        summary=digest_data.get("summary", ""),
        highlights=json.dumps(digest_data.get("highlights", [])),
        action_items=json.dumps(digest_data.get("action_items", [])),
        raw_stats=json.dumps({
            **digest_data,
            "total_commits": activity.total_commits,
            "total_prs_merged": activity.total_prs_merged,
            "total_issues_closed": activity.total_issues_closed,
            "contributors": activity.contributors,
        }),
        email_sent=False,
    )
    db.add(digest)
    db.commit()
    db.refresh(digest)

    # Send email in background
    if payload.send_email:
        background_tasks.add_task(
            _send_email_task,
            digest_id=digest.id,
            to_email=repo.notify_email,
            digest_data=digest_data,
            repo_full_name=repo.full_name,
            period_days=payload.period_days,
            stats={
                "total_commits": activity.total_commits,
                "total_prs_merged": activity.total_prs_merged,
                "total_issues_closed": activity.total_issues_closed,
                "contributors": activity.contributors,
            },
            db_url=str(db.bind.url),
        )

    return {
        "digest_id": digest.id,
        "summary": digest_data.get("summary"),
        "overall_health": digest_data.get("overall_health"),
        "highlights": digest_data.get("highlights", []),
        "action_items": digest_data.get("action_items", []),
        "email_queued": payload.send_email,
    }


def _send_email_task(
    digest_id: int,
    to_email: str,
    digest_data: dict,
    repo_full_name: str,
    period_days: int,
    stats: dict,
    db_url: str,
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    sent = email_service.send_digest(
        to_email=to_email,
        digest=digest_data,
        repo=repo_full_name,
        period=period_days,
        stats=stats,
    )

    digest = db.query(Digest).filter_by(id=digest_id).first()
    if digest:
        digest.email_sent = sent
        db.commit()
    db.close()
