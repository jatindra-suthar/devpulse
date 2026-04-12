from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.models import Repository
from app.services.github_service import github_service

router = APIRouter(prefix="/repos", tags=["repositories"])


class RepoCreate(BaseModel):
    owner: str
    name: str
    notify_email: EmailStr


class RepoOut(BaseModel):
    id: int
    owner: str
    name: str
    full_name: str
    description: str | None
    notify_email: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[RepoOut])
def list_repos(db: Session = Depends(get_db)):
    return db.query(Repository).all()


@router.post("/", response_model=RepoOut)
def add_repo(payload: RepoCreate, db: Session = Depends(get_db)):
    # Validate repo exists on GitHub
    info = github_service.validate_repo(payload.owner, payload.name)
    print(info)
    if not info["valid"]:
        raise HTTPException(status_code=404, detail="Repository not found on GitHub")

    existing = db.query(Repository).filter_by(
        full_name=f"{payload.owner}/{payload.name}"
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Repository already added")

    repo = Repository(
        owner=payload.owner,
        name=payload.name,
        full_name=f"{payload.owner}/{payload.name}",
        description=info.get("description"),
        notify_email=payload.notify_email,
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.delete("/{repo_id}")
def remove_repo(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter_by(id=repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(repo)
    db.commit()
    return {"ok": True}
