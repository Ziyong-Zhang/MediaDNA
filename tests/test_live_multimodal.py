import asyncio

import pytest

from backend.agents.deconstructor import DeconstructorAgent
from backend.schemas.beat_sheet import BeatSheet
from backend.services.media_service import cleanup_file, download_youtube_audio


@pytest.mark.live
def test_live_multimodal_extraction() -> None:
    """Live Tier 3 integration test for F10 Multimodal Pipeline."""
    # 19-second "Me at the zoo" video - perfect for fast, low-cost testing
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    print(f"\n[*] Downloading live audio from: {url}")
    media_path = download_youtube_audio(url)
    
    try:
        agent = DeconstructorAgent()
        prompt = (
            "Analyze this historical first YouTube video. "
            "Identify the hook, the pacing, and the key events."
        )
        
        print("[*] Uploading inline bytes to Gemini 1.5 Pro and extracting Beat Sheet...")
        beat_sheet = asyncio.run(
            agent.extract_beat_sheet(text_content=prompt, media_path=media_path)
        )
        
        # Verify the pipeline worked and correctly mapped to the Pydantic schema
        assert isinstance(beat_sheet, BeatSheet)
        assert beat_sheet.title is not None
        assert len(beat_sheet.beats) > 0
        
        # Print the output to the console so we can visually verify the "Wow" factor
        print("\n=== 🎬 MULTIMODAL BEAT SHEET GENERATED ===")
        print(beat_sheet.model_dump_json(indent=2))
        print("===========================================\n")
        
    finally:
        cleanup_file(media_path)
        print("[*] Local temporary file cleaned up.")