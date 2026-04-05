from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


VideoStatus = Literal[
    "uploaded",
    "queued",
    "processing",
    "converting",
    "uploading",
    "completed",
    "failed",
]


class UploadResponse(BaseModel):
    status: Literal["success"]
    video_id: str
    queue_status: Literal["queued"]


class VideoResponse(BaseModel):
    id: str
    status: str
    input_path: str
    output_path: str | None = None
    error: str | None = None
    retry_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None


class VideoUpdateResponse(BaseModel):
    status: Literal["updated"]
    video_id: str
    current_status: str


class VideoPatchRequest(BaseModel):
    status: VideoStatus
    output_path: str | None = None
    error: str | None = None
    retry_count: int | None = Field(default=None, ge=0)


class VideoDownloadResponse(BaseModel):
    video_id: str
    download_url: str
    expires_in: int
