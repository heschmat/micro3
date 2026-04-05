import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship



from app.db import Base


class User(Base):
    __tablename__ = "users"

    # String UUID primary key for users.
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Users log in with email.
    email = Column(String, unique=True, nullable=False, index=True)

    # Store hashed password only.
    password_hash = Column(String, nullable=False)

    # Convenience relationship to uploaded videos.
    videos = relationship("Video", back_populates="user")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, nullable=False, default="uploaded")
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    error = Column(String, nullable=True)

    retry_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Each video belongs to one user.
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="videos")

    def mark_status(
        self,
        *,
        status: str,
        output_path: str | None = None,
        error: str | None = None,
        retry_count: int | None = None,
    ) -> None:
        now = datetime.utcnow()

        self.status = status

        if output_path is not None:
            self.output_path = output_path

        if error is not None:
            self.error = error
        elif status != "failed":
            self.error = None

        if retry_count is not None:
            self.retry_count = retry_count

        if status in {"processing", "converting", "uploading"} and self.started_at is None:
            self.started_at = now

        if status == "completed":
            self.completed_at = now
            self.failed_at = None

        if status == "failed":
            self.failed_at = now
