import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, nullable=False, default="uploaded")
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
