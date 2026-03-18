from fastapi import FastAPI, UploadFile, File
import uuid

from app.storage import upload_file
from app.queue import publish_message
from app.logger import setup_logger

logger = setup_logger()

app = FastAPI()


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
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
        file_path = file_name  # inside "videos" bucket

        logger.info(f"Received upload: {file.filename}")
        logger.info(f"Generated video_id: {video_id}")

        # Upload to MinIO
        upload_file(file.file, file_path)

        # Create event
        message = {
            "video_id": video_id,
            "file_path": file_path,
            "output_format": "mp3",
        }

        # Send to queue
        publish_message(message)

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
