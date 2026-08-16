import logging
import os
import tempfile
from pathlib import Path

import yt_dlp  # type: ignore

logger = logging.getLogger(__name__)


def get_temp_dir() -> Path:
    """Get or create designated temporary directory for MediaDNA."""
    temp_dir = Path(tempfile.gettempdir()) / "mediadna"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def download_youtube_audio(url: str, max_duration_sec: int = 600) -> Path:
    """Download best audio stream from YouTube URL.

    Checks video duration before downloading.
    Raises ValueError if duration exceeds max_duration_sec.
    Returns Path to the downloaded audio file.
    """
    ydl_opts_info = {
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise ValueError(f"Failed to extract video info: {e}")

        if not info:
            raise ValueError("No video information found.")

        duration = info.get("duration")
        if duration is not None and duration > max_duration_sec:
            raise ValueError("Video exceeds maximum duration limit of 10 minutes.")

    # Designate temporary directory and a unique output template
    temp_dir = get_temp_dir()
    
    # We configure yt-dlp to prioritize native m4a, fallback to best audio.
    # We purposefully remove the 'FFmpegExtractAudio' postprocessor to avoid 
    # requiring ffmpeg system binaries in our GCP Cloud Run container.
    # Gemini 1.5 Pro natively supports .webm and .m4a formats.
    ydl_opts_download = {
        "format": "m4a/bestaudio/best",
        "outtmpl": str(temp_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise ValueError("Download failed, no info returned.")
            
            # The actual downloaded file might have changed extension due to postprocessing
            # Or we can query the output path.
            # Let's inspect the requested/expected output path.
            video_id = info.get("id")
            if not video_id:
                raise ValueError("Could not determine video ID from YouTube metadata.")
            
            # Since FFmpegExtractAudio extracts/converts to m4a (or whichever is preferred),
            # let's find the actual written file in temp_dir.
            # Usually it will be video_id.m4a or similar.
            # Let's check for video_id.*
            downloaded_files = list(temp_dir.glob(f"{video_id}.*"))
            if not downloaded_files:
                raise ValueError("Download succeeded but output file could not be found.")
            
            # Return the first matching file
            return downloaded_files[0]
            
        except yt_dlp.utils.DownloadError as e:
            raise ValueError(f"Failed to download audio: {e}")


def save_uploaded_file(file_bytes: bytes, filename: str) -> Path:
    """Save raw bytes from uploaded file securely to the temporary directory.

    Returns the local pathlib.Path.
    """
    temp_dir = get_temp_dir()
    # Secure filename (strip directory components to prevent path traversal)
    safe_name = Path(filename).name
    output_path = temp_dir / safe_name
    
    with open(output_path, "wb") as f:
        f.write(file_bytes)
        
    return output_path


def cleanup_file(path: Path) -> None:
    """Safely remove the file if it exists, catching any OSError with debug logging."""
    try:
        if path.exists():
            os.remove(path)
            logger.debug(f"Successfully cleaned up temporary file: {path}")
    except OSError as e:
        logger.debug(f"Failed to cleanup temporary file {path}: {e}")
