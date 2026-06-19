from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # YouTube Video ID
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued, downloading, transcribing, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    transcriptions: Mapped[List["Transcription"]] = relationship(
        "Transcription", back_populates="video", cascade="all, delete-orphan"
    )
    chunks: Mapped[List["Chunk"]] = relationship(
        "Chunk", back_populates="video", cascade="all, delete-orphan"
    )


class Transcription(Base):
    __tablename__ = "transcriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("videos.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    segments: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # Segment dictionary containing word-level timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="transcriptions")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("videos.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(
        JSON, nullable=False
    )  # Stored as JSON float array for portability
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="chunks")
    triplets: Mapped[List["Triplet"]] = relationship(
        "Triplet", back_populates="chunk", cascade="all, delete-orphan"
    )


class Triplet(Base):
    __tablename__ = "triplets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chunks.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    predicate: Mapped[str] = mapped_column(String(128), nullable=False)
    object: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    chunk: Mapped["Chunk"] = relationship("Chunk", back_populates="triplets")
