import os
import tempfile

import yt_dlp

from src.infrastructure.storage.s3_client import s3_client


def download_youtube_audio(url: str) -> dict:
    """
    Downloads the best native audio stream of a YouTube video without transcoding (avoids ffmpeg dependency).
    Uploads the resulting file directly to MinIO 'audio-blobs' bucket.
    """
    # 1. Extract metadata
    ydl_opts_meta = {
        "extract_flat": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
        info = ydl.extract_info(url, download=False)
        video_id = info["id"]
        title = info.get("title", "Unknown Title")
        duration = info.get("duration", 0)

    # 2. Download raw audio (preferring m4a which has excellent compatibility)
    temp_dir = tempfile.gettempdir()
    # Use output template that preserves the original extension
    outtmpl = os.path.join(temp_dir, f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": outtmpl,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # 3. Find the downloaded file (since extension is resolved dynamically)
    downloaded_file = None
    for ext in ["m4a", "webm", "mp3", "wav", "ogg"]:
        candidate = os.path.join(temp_dir, f"{video_id}.{ext}")
        if os.path.exists(candidate):
            downloaded_file = candidate
            break

    if not downloaded_file:
        raise FileNotFoundError(
            f"Failed to find downloaded audio file for video ID {video_id} in {temp_dir}"
        )

    # 4. Upload to MinIO
    filename = os.path.basename(downloaded_file)
    s3_client.upload_file("audio-blobs", filename, downloaded_file)

    # 5. Clean up local temp file
    try:
        os.remove(downloaded_file)
    except OSError:
        pass

    return {
        "video_id": video_id,
        "title": title,
        "duration": duration,
        "object_name": filename,
    }
