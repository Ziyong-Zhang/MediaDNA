from unittest.mock import MagicMock, patch

import pytest

from backend.services.media_service import (
    cleanup_file,
    download_youtube_audio,
    get_temp_dir,
    save_uploaded_file,
)


def test_save_uploaded_file() -> None:
    # Verifies bytes are written to disk and cleanup works
    file_bytes = b"test audio content"
    filename = "test_upload_file.mp3"
    
    saved_path = save_uploaded_file(file_bytes, filename)
    
    assert saved_path.exists()
    assert saved_path.name == filename
    with open(saved_path, "rb") as f:
        assert f.read() == file_bytes
        
    cleanup_file(saved_path)
    assert not saved_path.exists()


@patch("yt_dlp.YoutubeDL")
def test_download_youtube_audio_duration_exceeded(mock_ytdl: MagicMock) -> None:
    # Verifies ValueError is raised when metadata duration > 600
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        "id": "123456",
        "duration": 601,
    }
    mock_ytdl.return_value.__enter__.return_value = mock_instance

    with pytest.raises(ValueError, match="Video exceeds maximum duration limit of 10 minutes."):
        download_youtube_audio("https://www.youtube.com/watch?v=123456")


@patch("yt_dlp.YoutubeDL")
def test_download_youtube_audio_success(mock_ytdl: MagicMock) -> None:
    # Verifies download flow returns valid Path
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        "id": "mock_id_123",
        "duration": 120,
    }
    mock_ytdl.return_value.__enter__.return_value = mock_instance

    # To simulate successful file creation in the download template path
    temp_dir = get_temp_dir()
    mock_file_path = temp_dir / "mock_id_123.m4a"
    mock_file_path.write_text("dummy media data")

    try:
        downloaded_path = download_youtube_audio("https://www.youtube.com/watch?v=mock_id_123")
        assert downloaded_path == mock_file_path
        assert downloaded_path.exists()
    finally:
        cleanup_file(mock_file_path)
