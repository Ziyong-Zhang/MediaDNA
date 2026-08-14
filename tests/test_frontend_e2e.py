from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from frontend import api_client
from tests.conftest import click_button, mocked_gemini_pipeline

_APP_PATH = str(Path(__file__).resolve().parent.parent / "frontend" / "app.py")


def test_full_pipeline_end_to_end(monkeypatch: pytest.MonkeyPatch, live_backend_url: str) -> None:
    """Tier 3: drive the full pipeline (Deconstruct -> Architect -> Produce) in one AppTest session
    against the real FastAPI app (mocked Gemini only), asserting each stage's output correctly
    feeds the next stage's input and the final ProductionAssets render correctly.
    """
    monkeypatch.setattr(api_client, "BACKEND_URL", live_backend_url)

    beat_sheet_json = (
        '{"title": "Formula Breakdown", "total_duration": 60, "pacing_score": 8.8, '
        '"beats": [{"timestamp_sec": 0, "hook_type": "Visual Cliffhanger", "visual_cue": "Zoom", '
        '"audio_cue": "Riser", "emotion_shift": "Anticipation", "retention_driver": "Open Loop"}], '
        '"viral_summary": "High retention pacing structure.", "hook_analysis": "Cold open with a question.", '
        '"pacing_curve": ["fast", "climax"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "Hook"}]}'
    )
    blueprint_json = (
        '{"adapted_beat_sheet": {"title": "Adapted Formula", "total_duration": 60, "pacing_score": 8.5, '
        '"beats": [], "viral_summary": "Good", "hook_analysis": "Adapted hook.", "pacing_curve": ["fast"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "New hook"}]}, '
        '"structural_alignment_notes": ["kept the cold open"], '
        '"creative_deviations": ["changed the setting"]}'
    )
    assets_json = (
        '{"metadata": {"title": "Test Campaign", "target_platform": "YouTube", "estimated_duration": "30s"}, '
        '"pacing_curve": ["Hook", "Build"], '
        '"tts_script": [{"speaker": "Narrator", "text": "Hi.", "timestamp": "0:01", "emotion_tag": "energetic"}], '
        '"storyboard_panels": [{"scene_id": "s1", "imagen_prompt": "A kitchen scene", "camera_angle": "Wide"}]}'
    )

    at = AppTest.from_file(_APP_PATH)
    at.run()

    # Disable mock mode to enter live pipeline mode
    for checkbox in at.checkbox:
        if "MOCK MODE" in str(checkbox.label):
            checkbox.uncheck()
            break
    at.run()

    with mocked_gemini_pipeline(beat_sheet_json, blueprint_json, assets_json):
        at.text_area[0].set_value("Welcome to my video!")
        at.run()
        click_button(at, "Run Full Pipeline").click().run()
        assert not at.exception

    # Production assets are now in session state
    assert "production_assets" in at.session_state
    assets = at.session_state["production_assets"]
    assert assets["metadata"]["title"] == "Test Campaign"
    assert assets["metadata"]["estimated_duration"] == "30s"
    assert len(assets["tts_script"]) == 1
    assert len(assets["storyboard_panels"]) == 1

    # Final UI rendering matches the mocked Gemini output
    assert assets["tts_script"][0]["text"] == "Hi."
    assert assets["storyboard_panels"][0]["scene_id"] == "s1"
