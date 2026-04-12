from datetime import datetime, timedelta
from dataclasses import dataclass

from github import Github, GithubException

from app.core.config import settings


@dataclass
class CommitSummary:
    sha: str
    author: str
    message: str
    date: str
    url: str


@dataclass
class PRSummary:
    number: int
    title: str
    author: str
    state: str
    created_at: str
    merged_at: str | None
    url: str
    labels: list[str]


@dataclass
class IssueSummary:
    number: int
    title: str
    author: str
    state: str
    created_at: str
    closed_at: str | None
    url: str
    labels: list[str]


@dataclass
class RepoActivity:
    repo_full_name: str
    period_days: int
    commits: list[CommitSummary]
    pull_requests: list[PRSummary]
    issues: list[IssueSummary]
    contributors: list[str]
    total_commits: int
    total_prs_opened: int
    total_prs_merged: int
    total_issues_opened: int
    total_issues_closed: int


class GitHubService:
    def __init__(self):
        self.client = Github(settings.github_token)

    def fetch_activity(self, owner: str, name: str, period_days: int = 7) -> RepoActivity:
        since = datetime.utcnow() - timedelta(days=period_days)

        try:
            repo = self.client.get_repo(f"{owner}/{name}")
        except GithubException as e:
            raise ValueError(f"Cannot access repo {owner}/{name}: {e}")

        # Commits
        commits = []
        contributors = set()
        for commit in repo.get_commits(since=since):
            author = commit.author.login if commit.author else "unknown"
            contributors.add(author)
            commits.append(
                CommitSummary(
                    sha=commit.sha[:7],
                    author=author,
                    message=commit.commit.message.split("\n")[0][:120],
                    date=commit.commit.author.date.isoformat(),
                    url=commit.html_url,
                )
            )

        # Pull Requests
        pull_requests = []
        prs_opened = 0
        prs_merged = 0
        for pr in repo.get_pulls(state="all", sort="created", direction="desc"):
            if pr.created_at < since and (pr.merged_at is None or pr.merged_at < since):
                break
            if pr.created_at >= since:
                prs_opened += 1
            if pr.merged_at and pr.merged_at >= since:
                prs_merged += 1
            pull_requests.append(
                PRSummary(
                    number=pr.number,
                    title=pr.title[:120],
                    author=pr.user.login,
                    state=pr.state,
                    created_at=pr.created_at.isoformat(),
                    merged_at=pr.merged_at.isoformat() if pr.merged_at else None,
                    url=pr.html_url,
                    labels=[l.name for l in pr.labels],
                )
            )

        # Issues (exclude PRs)
        issues = []
        issues_opened = 0
        issues_closed = 0
        for issue in repo.get_issues(state="all", since=since):
            if issue.pull_request:
                continue
            if issue.created_at >= since:
                issues_opened += 1
            if issue.closed_at and issue.closed_at >= since:
                issues_closed += 1
            issues.append(
                IssueSummary(
                    number=issue.number,
                    title=issue.title[:120],
                    author=issue.user.login,
                    state=issue.state,
                    created_at=issue.created_at.isoformat(),
                    closed_at=issue.closed_at.isoformat() if issue.closed_at else None,
                    url=issue.html_url,
                    labels=[l.name for l in issue.labels],
                )
            )

        return RepoActivity(
            repo_full_name=f"{owner}/{name}",
            period_days=period_days,
            commits=commits[:50],  # cap at 50 most recent
            pull_requests=pull_requests[:30],
            issues=issues[:30],
            contributors=list(contributors),
            total_commits=len(commits),
            total_prs_opened=prs_opened,
            total_prs_merged=prs_merged,
            total_issues_opened=issues_opened,
            total_issues_closed=issues_closed,
        )

    def validate_repo(self, owner: str, name: str) -> dict:
        try:
            print(f"Validating {owner}/{name}")
            repo = self.client.get_repo(f"{owner}/{name}")
            return {
                "valid": True,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "language": repo.language,
            }
        except GithubException:
            return {"valid": False}


github_service = GitHubService()
