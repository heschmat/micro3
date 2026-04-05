import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

from app.db import Base


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
