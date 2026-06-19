from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # YouTube Video ID
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")  # queued, downloading, transcribing, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transcriptions: Mapped[List["Transcription"]] = relationship(
        "Transcription", back_populates="video", cascade="all, delete-orphan"
    )


class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(50), ForeignKey("videos.id"), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    segments: Mapped[dict] = mapped_column(JSON, nullable=False)  # Segment dictionary containing word-level timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="transcriptions")
