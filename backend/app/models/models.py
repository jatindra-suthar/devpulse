from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notify_email: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    digests: Mapped[list["Digest"]] = relationship(
        "Digest", back_populates="repository", cascade="all, delete-orphan"
    )


class Digest(Base):
    __tablename__ = "digests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("repositories.id"), nullable=False
    )
    period_days: Mapped[int] = mapped_column(Integer, default=7)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[str] = mapped_column(Text, nullable=False)
    action_items: Mapped[str] = mapped_column(Text, nullable=True)
    raw_stats: Mapped[str] = mapped_column(Text, nullable=True)
    email_sent: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="digests")
