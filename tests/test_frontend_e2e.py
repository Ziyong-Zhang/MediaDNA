import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from frontend import api_client
from tests.conftest import click_button, mocked_gemini_pipeline

_APP_PATH = str(Path(__file__).resolve().parent.parent / "frontend" / "app.py")


def test_full_pipeline_end_to_end(monkeypatch: pytest.MonkeyPatch, live_backend_url: str) -> None:
    """Tier 3: drive Deconstructor -> Architect -> Director in one AppTest session against the
    real FastAPI app (mocked Gemini only), asserting each stage's output correctly feeds the next
    stage's input and the final rendering matches the mocked Gemini output.
    """
    monkeypatch.setattr(api_client, "BACKEND_URL", live_backend_url)

    beat_sheet_json = (
        '{"hook_analysis": "Cold open with a question.", '
        '"pacing_curve": ["fast", "climax"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "Hook"}]}'
    )
    blueprint_json = (
        '{"adapted_beat_sheet": {"hook_analysis": "Adapted hook.", "pacing_curve": ["fast"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "New hook"}]}, '
        '"structural_alignment_notes": ["kept the cold open"], '
        '"creative_deviations": ["changed the setting"]}'
    )
    assets_json = (
        '{"tts_script": [{"speaker": "Narrator", "text": "Hi.", "timestamp": "0:01"}], '
        '"visual_prompts": [{"scene_id": "s1", "prompt_text": "A kitchen", "style_tags": ["cinematic"]}], '
        '"metadata": {"duration": "30s"}}'
    )

    at = AppTest.from_file(_APP_PATH)
    at.run()

    with mocked_gemini_pipeline(beat_sheet_json, blueprint_json, assets_json):
        at.radio[0].set_value("Text Transcript/Script")
        at.run()
        at.text_area[0].set_value("Welcome to my video!")
        at.run()
        click_button(at, "Run Deconstructor").click().run()
        assert not at.exception

        at.text_area[1].set_value("Make it a cooking channel with a twist ending")
        at.run()
        click_button(at, "Run Architect").click().run()
        assert not at.exception

        click_button(at, "Run Director").click().run()
        assert not at.exception

    # Stage outputs correctly chained: architect received the deconstructor's real BeatSheet,
    # director received the architect's real Blueprint.
    assert at.session_state["beat_sheet"]["hook_analysis"] == "Cold open with a question."
    assert at.session_state["blueprint"]["structural_alignment_notes"] == ["kept the cold open"]
    assets = at.session_state["production_assets"]
    assert assets["metadata"]["duration"] == "30s"

    # Final UI rendering matches the mocked Gemini output for the last stage.
    tts_table = at.table[0].value.to_dict("records")
    visual_table = at.table[1].value.to_dict("records")
    metadata = json.loads(at.json[-1].value)
    assert tts_table == assets["tts_script"]
    assert visual_table == assets["visual_prompts"]
    assert metadata == assets["metadata"]
