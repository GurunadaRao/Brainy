from typing import Any, Dict, Tuple

from sqlalchemy import select

from src.domain.models import Transcription, Video
from src.infrastructure.database.session import AsyncSessionLocal


def format_seconds_to_timestamp(seconds: float) -> str:
    """Formats float seconds into MM:SS format (or HH:MM:SS if over an hour)."""
    if seconds is None:
        return "00:00"
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


async def get_chunk_timestamps(
    chunk_content: str, video_id: str
) -> Tuple[float, float]:
    """
    Finds the start and end seconds of a chunk's content by matching
    overlapping segments from the database transcription records.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Transcription).where(Transcription.video_id == video_id)
        result = await session.execute(stmt)
        transcriptions = result.scalars().all()
        if not transcriptions:
            return 0.0, 0.0

        segments = transcriptions[0].segments
        if not segments:
            return 0.0, 0.0

    # Heuristic: Find all segments that overlap with the chunk content.
    # We clean the text to make matching robust against punctuation and spacing.
    def clean_text(text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()

    import re

    cleaned_chunk = clean_text(chunk_content)

    matching_starts = []
    matching_ends = []

    for seg in segments:
        seg_text = seg.get("text", "")
        cleaned_seg = clean_text(seg_text)
        # If segment text overlaps with chunk content
        if cleaned_seg and (
            cleaned_seg in cleaned_chunk or cleaned_chunk in cleaned_seg
        ):
            matching_starts.append(seg.get("start", 0.0))
            matching_ends.append(seg.get("end", 0.0))

    if matching_starts and matching_ends:
        return min(matching_starts), max(matching_ends)

    # Fallback: if no overlapping matches, return default bounding values
    # of the first and last segments
    try:
        return segments[0].get("start", 0.0), segments[-1].get("end", 0.0)
    except Exception:
        return 0.0, 0.0


async def get_video_title(video_id: str) -> str:
    """Helper to fetch video title from database."""
    async with AsyncSessionLocal() as session:
        stmt = select(Video).where(Video.id == video_id)
        result = await session.execute(stmt)
        video = result.scalar_one_or_none()
        return video.title if video and video.title else "Unknown Video"


async def assemble_context(retrieved_data: Dict[str, Any]) -> str:
    """
    Assembles a dense, structured context block combining text chunks,
    timestamp citations, and graph triplets.
    """
    context_parts = []

    # 1. Add Text Source Chunks
    context_parts.append("=== RETRIEVED VIDEO TRANSCRIPT CHUNKS ===")
    for idx, chunk in enumerate(retrieved_data.get("chunks", [])):
        video_id = chunk["video_id"]
        title = await get_video_title(video_id)
        start, end = await get_chunk_timestamps(chunk["content"], video_id)

        start_ts = format_seconds_to_timestamp(start)
        end_ts = format_seconds_to_timestamp(end)

        context_parts.append(
            f"[Source {idx+1}: {title} - {start_ts} to {end_ts}]\n"
            f"Content: {chunk['content']}\n"
        )

    # 2. Add Graph Relationships
    context_parts.append("=== RETRIEVED KNOWLEDGE GRAPH FACTS ===")
    relationships = retrieved_data.get("relationships", [])
    if relationships:
        for rel in relationships:
            context_parts.append(
                f"({rel['subject']}) -[{rel['predicate']}]-> ({rel['object']})"
            )
    else:
        context_parts.append("No related graph entities found.")

    return "\n".join(context_parts)
