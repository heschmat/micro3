import os
import uuid

from sqlalchemy.orm import Session

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated

from app.storage import upload_file, generate_presigned_download_url
from app.queue import publish_message
from app.logger import setup_logger
from app.models import Video
from app.deps import get_db
from app.schemas import (
    UploadResponse,
    VideoPatchRequest,
    VideoResponse,
    VideoUpdateResponse,
    VideoDownloadResponse,
)
from app.config import settings

logger = setup_logger()

app = FastAPI(title="Upload Service")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_STATUSES = {
    "uploaded",
    "queued",
    "processing",
    "converting",
    "uploading",
    "completed",
    "failed",
}


def serialize_video(video: Video) -> VideoResponse:
    """
    Convert a SQLAlchemy Video model into the public API response shape.
    """
    return VideoResponse(
        id=video.id,
        status=video.status,
        input_path=video.input_path,
        output_path=video.output_path,
        error=video.error,
        retry_count=video.retry_count,
        created_at=video.created_at,
        updated_at=video.updated_at,
        started_at=video.started_at,
        completed_at=video.completed_at,
        failed_at=video.failed_at,
    )


def validate_upload_file(file: UploadFile) -> None:
    """
    Perform basic upload validation before attempting storage or DB writes.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if "." not in file.filename:
        raise HTTPException(status_code=400, detail="File must have an extension")

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Preserve the current cursor position, inspect file size,
    # then restore the cursor so upload still works correctly.
    current_pos = file.file.tell()
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(current_pos)

    if size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed is {settings.MAX_UPLOAD_SIZE_MB} MB",
        )


@app.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a source video, store it in object storage,
    create a DB record, and publish a conversion job.
    """
    validate_upload_file(file)

    try:
        # Generate a stable job ID first so it can be used across
        # storage, DB, and queue payloads.
        video_id = str(uuid.uuid4())

        # Preserve the original file extension in storage.
        file_extension = file.filename.rsplit(".", 1)[-1].lower()
        file_name = f"{video_id}.{file_extension}"
        file_path = file_name

        logger.info("Received upload: %s", file.filename)
        logger.info("Generated video_id: %s", video_id)

        # 1) Upload the raw file to object storage.
        upload_file(file.file, file_path)

        # 2) Create the initial DB record.
        video = Video(
            id=video_id,
            status="uploaded",
            input_path=file_path,
        )

        db.add(video)
        db.commit()
        db.refresh(video)

        # 3) Publish a conversion job.
        message = {
            "video_id": video_id,
            "file_path": file_path,
            "output_format": "mp3",
            "retry_count": 0,
        }
        publish_message(message)

        # 4) Mark the job as queued after the message is accepted.
        video.mark_status(status="queued")
        db.commit()
        db.refresh(video)

        logger.info("Video %s queued successfully", video_id)

        return UploadResponse(
            status="success",
            video_id=video_id,
            queue_status="queued",
        )

    except HTTPException:
        # Preserve explicit HTTP errors unchanged.
        db.rollback()
        raise
    except Exception:
        # Roll back the DB transaction and return a proper server error.
        db.rollback()
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail="Upload failed")


@app.patch("/videos/{video_id}", response_model=VideoUpdateResponse)
def update_video(
    video_id: str,
    db: Session = Depends(get_db),
    payload: Annotated[VideoPatchRequest | None, Body()] = None,
    status: str | None = None,
    output_path: str | None = None,
    error: str | None = None,
    retry_count: int | None = None,
):
    """
    Update a video's processing status.

    Backward-compatible:
    - accepts JSON body from newer clients
    - also accepts query params from older worker services
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Prefer JSON body when provided.
    if payload is not None:
        next_status = payload.status
        next_output_path = payload.output_path
        next_error = payload.error
        next_retry_count = payload.retry_count
    else:
        # Fallback to query params for older workers.
        if status is None:
            raise HTTPException(
                status_code=400,
                detail="Either JSON body or status query param is required",
            )

        next_status = status
        next_output_path = output_path
        next_error = error
        next_retry_count = retry_count

    if next_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    video.mark_status(
        status=next_status,
        output_path=next_output_path,
        error=next_error,
        retry_count=next_retry_count,
    )

    db.commit()
    db.refresh(video)

    logger.info(
        "Video %s updated: status=%s, output_path=%s, error=%s, retry_count=%s",
        video_id,
        video.status,
        video.output_path,
        video.error,
        video.retry_count,
    )

    return VideoUpdateResponse(
        status="updated",
        video_id=video.id,
        current_status=video.status,
    )


@app.get("/videos/{video_id}", response_model=VideoResponse)
def get_video(video_id: str, db: Session = Depends(get_db)):
    """
    Return the current state of a single video job.
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Not found")

    return serialize_video(video)


@app.get("/videos/{video_id}/download", response_model=VideoDownloadResponse)
def get_video_download(video_id: str, db: Session = Depends(get_db)):
    """
    Generate a fresh presigned download URL for a completed MP3.

    This keeps download authorization and job state checks behind the
    upload-service, which already owns the video job record.
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status != "completed":
        raise HTTPException(status_code=409, detail="Audio not ready")

    if not video.output_path:
        raise HTTPException(status_code=409, detail="Output file path is missing")

    try:
        download_url = generate_presigned_download_url(
            object_name=video.output_path,
            expires_in=settings.DOWNLOAD_URL_EXPIRES_SECONDS,
        )
    except Exception:
        logger.exception("Failed to generate download URL for video_id=%s", video_id)
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

    return VideoDownloadResponse(
        video_id=video.id,
        download_url=download_url,
        expires_in=settings.DOWNLOAD_URL_EXPIRES_SECONDS,
    )
