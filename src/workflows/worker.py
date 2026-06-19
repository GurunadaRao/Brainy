import asyncio
import json
import os
import sys
import tempfile
from typing import Any, Dict

from sqlalchemy import select

# Ensure import works
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.configs.settings import settings  # noqa: E402
from src.domain.models import Transcription, Video  # noqa: E402
from src.infrastructure.database.session import (  # noqa: E402
    AsyncSessionLocal,
    with_retry,
)
from src.infrastructure.queue.rabbitmq_client import rabbitmq_client  # noqa: E402
from src.infrastructure.storage.s3_client import s3_client  # noqa: E402
from src.ingestion.downloader import download_youtube_audio  # noqa: E402


# --- Database Helpers ---
@with_retry()
async def db_update_video_status(
    video_id: str,
    status: str,
    title: str | None = None,
    duration: int | None = None,
) -> None:

    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(Video).where(Video.id == video_id)
            result = await session.execute(stmt)
            video = result.scalar_one_or_none()
            if not video:
                # If not exists (e.g. first trigger), create it
                video = Video(
                    id=video_id, url=f"https://www.youtube.com/watch?v={video_id}"
                )
                session.add(video)
            video.status = status
            if title:
                video.title = title
            if duration:
                video.duration = duration


@with_retry()
async def db_save_transcription(video_id: str, data: Dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            transcription = Transcription(
                video_id=video_id,
                text=data["text"],
                language=data.get("language", "en"),
                segments=data["segments"],
            )
            session.add(transcription)


# --- Whisper Ingestion Logic ---
def run_transcription(file_path: str) -> Dict[str, Any]:
    """Transcribes audio file using OpenAI Whisper API or falls back to mock data."""
    if settings.OPENAI_API_KEY == "mock-key" or not settings.OPENAI_API_KEY:
        print("Whisper: Running mock transcription...")
        return {
            "text": "Hello, welcome to Brainy 1.0. This is a mock transcription of the YouTube video.",
            "language": "en",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 3.0,
                    "text": "Hello, welcome to Brainy 1.0.",
                    "words": [
                        {"word": "Hello,", "start": 0.0, "end": 0.5},
                        {"word": "welcome", "start": 0.5, "end": 1.0},
                        {"word": "to", "start": 1.0, "end": 1.2},
                        {"word": "Brainy", "start": 1.2, "end": 1.8},
                        {"word": "1.0.", "start": 1.8, "end": 3.0},
                    ],
                },
                {
                    "id": 1,
                    "start": 3.0,
                    "end": 7.0,
                    "text": "This is a mock transcription of the YouTube video.",
                    "words": [
                        {"word": "This", "start": 3.0, "end": 3.5},
                        {"word": "is", "start": 3.5, "end": 3.8},
                        {"word": "a", "start": 3.8, "end": 4.0},
                        {"word": "mock", "start": 4.0, "end": 4.5},
                        {"word": "transcription", "start": 4.5, "end": 5.5},
                        {"word": "of", "start": 5.5, "end": 5.8},
                        {"word": "the", "start": 5.8, "end": 6.0},
                        {"word": "YouTube", "start": 6.0, "end": 6.5},
                        {"word": "video.", "start": 6.5, "end": 7.0},
                    ],
                },
            ],
        }
    else:
        print("Whisper: Querying OpenAI Whisper API...")
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        with open(file_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
            )
            # Response formatting
            return {
                "text": getattr(transcript_response, "text", ""),
                "language": getattr(transcript_response, "language", "en"),
                "segments": getattr(transcript_response, "segments", []),
            }


# --- Queue Callbacks ---
def handle_download(msg: Dict[str, Any]) -> None:
    url = msg.get("url")
    video_id = msg.get("video_id")
    if not url or not video_id:
        print("Worker Error: Missing url or video_id in message.")
        return

    print(f"Ingestion Worker: Starting download for video {video_id}...")
    asyncio.run(db_update_video_status(video_id, "downloading"))

    try:
        # Download audio stream to MinIO
        res = download_youtube_audio(url)
        safe_title = res["title"].encode("ascii", "ignore").decode("ascii")
        print(f"Ingestion Worker: Successfully downloaded {video_id} - '{safe_title}'")

        # Update database with details
        asyncio.run(
            db_update_video_status(
                video_id=video_id,
                status="transcribing",
                title=res["title"],
                duration=res["duration"],
            )
        )

        # Publish transcription task
        rabbitmq_client.publish(
            "video_transcription",
            {"video_id": video_id, "object_name": res["object_name"]},
        )
    except Exception as e:
        print(f"Ingestion Worker Error: Failed to ingest video {video_id}: {e}")
        asyncio.run(db_update_video_status(video_id, "failed"))
        raise


def handle_transcription(msg: Dict[str, Any]) -> None:
    video_id = msg.get("video_id")
    object_name = msg.get("object_name")
    if not video_id or not object_name:
        print("Transcription Worker Error: Missing fields.")
        return

    print(f"Transcription Worker: Processing {video_id}...")

    temp_dir = tempfile.gettempdir()
    local_path = os.path.join(temp_dir, object_name)

    try:
        # 1. Download file from MinIO local storage
        s3_client.download_file("audio-blobs", object_name, local_path)

        # 2. Run Whisper Transcription
        transcript_data = run_transcription(local_path)

        # 3. Save to database
        asyncio.run(db_save_transcription(video_id, transcript_data))

        # 4. Save JSON transcript metadata file to MinIO
        transcript_json_bytes = json.dumps(transcript_data, indent=2).encode("utf-8")
        # Uploading bytes as a file wrapper
        import io

        s3_client.upload_stream(
            bucket_name="transcripts",
            object_name=f"{video_id}_transcript.json",
            data=io.BytesIO(transcript_json_bytes),
            length=len(transcript_json_bytes),
        )

        # 5. Update Status
        asyncio.run(db_update_video_status(video_id, "completed"))
        print(f"Transcription Worker: Completed transcription for {video_id}")
    except Exception as e:
        print(f"Transcription Worker Error: Failed for {video_id}: {e}")
        asyncio.run(db_update_video_status(video_id, "failed"))
        raise
    finally:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass


if __name__ == "__main__":
    worker_type = sys.argv[1] if len(sys.argv) > 1 else "download"
    if worker_type == "download":
        rabbitmq_client.start_consumer("video_ingestion", handle_download)
    elif worker_type == "transcribe":
        rabbitmq_client.start_consumer("video_transcription", handle_transcription)
    else:
        print(f"Unknown worker type: {worker_type}")
