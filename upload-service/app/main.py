import uuid

from sqlalchemy.orm import Session

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.storage import upload_file
from app.queue import publish_message
from app.logger import setup_logger
from app.models import Video
from app.deps import get_db

logger = setup_logger()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload endpoint:
    - receives file
    - uploads to MinIO
    - sends event to RabbitMQ
    """

    try:
        # Generate unique ID
        video_id = str(uuid.uuid4())

        # Define storage path
        file_extension = file.filename.split(".")[-1]
        file_name = f"{video_id}.{file_extension}"
        file_path = file_name  # inside "videos" 

        logger.info(f"Received upload: {file.filename}")
        logger.info(f"Generated video_id: {video_id}")

        # 1. upload first: upload to MinIO
        upload_file(file.file, file_path)

        # 2. insert DB
        video = Video(
            id=video_id,
            status="uploaded",
            input_path=file_path
        )

        db.add(video)
        db.commit()

        # 3. publish message
        # Create event
        message = {
            "video_id": video_id,
            "file_path": file_path,
            "output_format": "mp3",
            "retry_count": 0,
        }

        # Send to queue
        publish_message(message)

        # 4. Update status to queued
        video.status = "queued"
        db.commit()

        logger.info(f"Video {video_id} queued successfully, status=queued")

        return {
            "status": "success",
            "video_id": video_id,
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {
            "status": "error",
            "message": str(e),
        }


@app.patch("/videos/{video_id}")
def update_video(
    video_id: str,
    status: str,
    output_path: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = status
    # only overwrite if explicitly provided
    if output_path is not None:
        video.output_path = output_path

    if error is not None:
        video.error = error

    db.commit()

    logger.info(
        f"Video {video_id} updated: status={status}, output_path={output_path}, error={error}"
    )

    return {"status": "updated"}


@app.get("/videos/{video_id}")
def get_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "id": video.id,
        "status": video.status,
        "input_path": video.input_path,
        "output_path": video.output_path,
        "error": video.error,
        "created_at": video.created_at.isoformat() if video.created_at else None,
        "updated_at": video.updated_at.isoformat() if video.updated_at else None,
    }
