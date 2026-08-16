"""Streamlit UI for MediaDNA: Viral Pre-Production Engine Dashboard.

A cinematic dashboard showcasing Director agent output (Imagen 3 storyboard prompts
and Gemini TTS scripts) with a mock mode for offline prototyping and live backend fallback.
"""

from typing import Any

import streamlit as st

from frontend import api_client
from frontend.api_client import BackendError

# Configure page layout
st.set_page_config(
    page_title="MediaDNA: Viral Pre-Production Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Sidebar Controls
# ============================================================================
st.sidebar.title("⚙️ Viral Pre-Production Engine")
st.sidebar.divider()

# Mock Mode Toggle
mock_mode: bool = st.sidebar.checkbox(
    "🎬 MOCK MODE (Bypass API limits)",
    value=True,
    help="When enabled, directly injects a cinematic hiking-boots-themed production asset set. When disabled, calls the real backend API.",
)

if mock_mode:
    st.sidebar.info("✨ Mock mode active: Using canned cinematic production assets (hiking boots trailer theme).")
else:
    st.sidebar.info("🔗 Live mode active: Real backend API calls enabled. Ensure backend is running on port 8000.")

# ============================================================================
# Header
# ============================================================================
st.title("🎥 MediaDNA: Viral Pre-Production Engine")
st.markdown("**Agentic Cinema Hackathon** — Transform raw media into polished production assets with Imagen 3 visuals and Gemini TTS voice.")

# ============================================================================
# Mock Data: High-Energy Hiking Boots Trailer Theme
# ============================================================================
def create_mock_production_assets() -> dict[str, Any]:
    """Generate a cinematic ProductionAssets dict for outdoor hiking boots.
    
    Strictly conforms to the ProductionAssets Pydantic schema:
    - metadata: dict[str, str]
    - pacing_curve: list[str]
    - tts_script: list[TTSLine]  (speaker, text, timestamp, emotion_tag)
    - storyboard_panels: list[StoryboardPanel]  (scene_id, imagen_prompt, camera_angle)
    """
    return {
        "metadata": {
            "title": "Conquer the Trail: Premium Hiking Boot Campaign",
            "target_platform": "YouTube Shorts / TikTok",
            "estimated_duration": "45 seconds",
            "style": "High-energy outdoor adventure",
            "target_audience": "Adventure seekers, outdoor enthusiasts, 18-45 years old",
        },
        "pacing_curve": [
            "Cold open: Dramatic mountain vista",
            "Fast hook: Hero boot conquers rocky terrain",
            "Tension build: Steep cliff edge, adrenaline spike",
            "Emotional peak: Summit victory, golden hour light",
            "Call-to-action: Product reveal with tech specs",
            "Payoff: Community testimonial montage",
        ],
        "tts_script": [
            {
                "speaker": "Narrator (Epic Voiceover)",
                "text": "When the trail gets treacherous, your boot shouldn't.",
                "timestamp": "00:00-00:05",
                "emotion_tag": "energetic, commanding",
            },
            {
                "speaker": "Narrator (Epic Voiceover)",
                "text": "SummitForce Boots: Carbon-fiber ankle support. All-terrain grip. Built for the impossible.",
                "timestamp": "00:05-00:15",
                "emotion_tag": "confident, powerful",
            },
            {
                "speaker": "Narrator (Epic Voiceover)",
                "text": "Watch Sarah climb 3,000 vertical feet in a single day.",
                "timestamp": "00:15-00:20",
                "emotion_tag": "inspiring",
            },
            {
                "speaker": "Sarah (Testimonial)",
                "text": "These boots changed everything. I felt invincible.",
                "timestamp": "00:20-00:25",
                "emotion_tag": "authentic, breathless",
            },
            {
                "speaker": "Narrator (Epic Voiceover)",
                "text": "SummitForce. Conquer every trail. Shop now.",
                "timestamp": "00:25-00:30",
                "emotion_tag": "authoritative, call-to-action",
            },
        ],
        "storyboard_panels": [
            {
                "scene_id": "OPEN_001",
                "imagen_prompt": "Ultra-cinematic wide shot of a snow-capped mountain range at golden hour, dramatic clouds, epic landscape photography, 8K, vibrant colors, professional outdoor adventure cinematography",
                "camera_angle": "Wide drone shot, ascending slowly, cinematic lighting from the left, golden hour backlight",
            },
            {
                "scene_id": "HERO_002",
                "imagen_prompt": "Close-up macro shot of a premium hiking boot sole gripping weathered black volcanic rock, water droplets on the boot, sharp focus on tread pattern, professional product photography",
                "camera_angle": "Extreme close-up, macro lens, 45-degree angle, tactical lighting highlighting boot texture",
            },
            {
                "scene_id": "CLIMB_003",
                "imagen_prompt": "Cinematic action shot of a hiker ascending a steep rocky mountain face in daylight, dramatic shadows, adventure photography style, high energy, professional outdoor cinematography",
                "camera_angle": "Medium shot, handheld-style dynamic movement, following the climber from the side, natural sunlight",
            },
            {
                "scene_id": "SUMMIT_004",
                "imagen_prompt": "Epic summit moment: hiker standing triumphantly at mountain peak, arms raised, golden hour sunlight, vast landscape backdrop, cinematic celebration, professional adventure photography",
                "camera_angle": "Wide shot from below, low-angle heroic framing, golden hour lighting from behind, slow pan to reveal landscape",
            },
            {
                "scene_id": "PRODUCT_005",
                "imagen_prompt": "Premium product shot: SummitForce hiking boot centered on a white studio background with dramatic shadows, showing sole, ankle support design, professional commercial product photography, 8K resolution",
                "camera_angle": "3D product rotation, 45-degree angle, studio lighting with key and fill lights, pure white backdrop",
            },
            {
                "scene_id": "TESTIMONIAL_006",
                "imagen_prompt": "Portrait of a smiling hiker named Sarah in natural outdoor setting, wearing hiking gear, backlit by golden hour sunlight, authentic testimonial style photography, warm and inviting",
                "camera_angle": "Medium close-up, eye-level, soft natural lighting, shallow depth of field, authentic documentary style",
            },
        ],
    }


# ============================================================================
# Main Content Area
# ============================================================================

production_assets: dict[str, Any] | None = None

if mock_mode:
    # In mock mode, directly inject the mock assets into session_state
    if "production_assets" not in st.session_state:
        st.session_state.production_assets = create_mock_production_assets()
    production_assets = st.session_state.production_assets
    st.success("✨ Mock Production Assets loaded. Ready to preview!")
else:
    # Live mode: Wire to backend
    st.header("📝 Step 1: Deconstruction Pipeline")

    # Input transcript (optional text content for the agent prompt)
    transcript_text: str = st.text_area(
        "Additional Context or Transcript (Optional)",
        height=200,
        placeholder="Paste your video/audio transcript or creative script here...",
    )

    # Reference media input via tabs
    st.markdown("### Reference Media (Optional)")
    tab1, tab2 = st.tabs(["YouTube URL", "Upload File"])

    with tab1:
        youtube_url: str = st.text_input("YouTube URL", key="youtube_url")

    with tab2:
        uploaded_file = st.file_uploader(
            "Upload media file (.mp3, .m4a, .mp4)",
            type=["mp3", "m4a", "mp4"],
        )

    # Run full pipeline
    if st.button("🚀 Run Full Pipeline (Deconstruct → Architect → Produce)", type="primary"):
        if not transcript_text and not youtube_url and uploaded_file is None:
            st.error("Please provide a transcript, a YouTube URL, or an uploaded media file to proceed.")
        else:
            try:
                with st.spinner("🔄 Deconstructing reference media..."):
                    if uploaded_file is not None:
                        beat_sheet_data = api_client.deconstruct(
                            transcript_text,
                            file_bytes=uploaded_file.getvalue(),
                            file_name=uploaded_file.name,
                        )
                    elif youtube_url:
                        beat_sheet_data = api_client.deconstruct(
                            transcript_text,
                            reference_url=youtube_url,
                        )
                    else:
                        beat_sheet_data = api_client.deconstruct(transcript_text)

                with st.spinner("🎨 Architecting creative blueprint..."):
                    creative_brief = st.text_input(
                        "Creative Brief (for this demo session)",
                        value="High-energy outdoor adventure product campaign",
                    )
                    blueprint_data = api_client.architect(beat_sheet_data, creative_brief)

                with st.spinner("🎬 Producing cinematic assets..."):
                    production_assets_data = api_client.produce(blueprint_data)

                st.session_state.production_assets = production_assets_data
                st.success("✨ Production Assets generated successfully!")

            except BackendError as e:
                st.error(f"❌ Backend error: {e}")
            except TimeoutError as e:
                st.error(f"❌ Connection timeout: {e}")
            except ValueError as e:
                st.error(f"❌ Invalid response format: {e}")
    
    # Check if we have production assets to render
    if "production_assets" in st.session_state:
        production_assets = st.session_state.production_assets
    else:
        st.info("👆 Enter a transcript above and click 'Run Full Pipeline' to begin.")


# ============================================================================
# Render Production Assets (if available)
# ============================================================================

if production_assets is not None:
    st.divider()
    st.header("📊 Production Assets Dashboard")
    
    # ========== Metadata Header ==========
    st.subheader("📋 Production Metadata")
    metadata = production_assets.get("metadata", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Title", metadata.get("title", "N/A"))
    with col2:
        st.metric("Platform", metadata.get("target_platform", "N/A"))
    with col3:
        st.metric("Duration", metadata.get("estimated_duration", "N/A"))
    
    # Display additional metadata in an expander
    with st.expander("📌 Expand Full Metadata"):
        for key, value in metadata.items():
            st.write(f"**{key}**: {value}")
    
    # ========== Pacing Curve ==========
    st.subheader("📈 Pacing & Emotional Curve")
    pacing_curve: list[str] = production_assets.get("pacing_curve", [])
    
    # Render as a stylized step sequence
    for idx, pacing_point in enumerate(pacing_curve, 1):
        col_num, col_desc = st.columns([0.5, 4])
        with col_num:
            st.markdown(f"### **{idx}**")
        with col_desc:
            st.markdown(f"_{pacing_point}_", help=f"Pacing point {idx}")
    
    st.divider()
    
    # ========== Two-Column Layout: TTS Script + Storyboard ==========
    left_col, right_col = st.columns(2)
    
    # ========== LEFT COLUMN: TTS Script ==========
    with left_col:
        st.subheader("🎤 Gemini TTS Script")
        st.markdown("*Narration and dialogue formatted for Gemini Text-to-Speech synthesis*")
        
        tts_script: list[dict[str, str]] = production_assets.get("tts_script", [])
        
        for idx, line in enumerate(tts_script, 1):
            with st.container(border=True):
                speaker = line.get("speaker", "Unknown")
                text = line.get("text", "")
                timestamp = line.get("timestamp", "")
                emotion_tag = line.get("emotion_tag", "")
                
                # Display speaker and timestamp as a header
                st.markdown(f"**{speaker}** ⏱️ `{timestamp}`")
                
                # Display emotion tag as a small badge
                st.caption(f"🎵 Tone: _{emotion_tag}_")
                
                # Display the actual dialogue text
                st.markdown(f"> {text}")
    
    # ========== RIGHT COLUMN: Storyboard Prompts ==========
    with right_col:
        st.subheader("🎨 Imagen 3 Storyboard Prompts")
        st.markdown("*High-fidelity prompts optimized for Imagen 3 image generation*")
        
        storyboard_panels: list[dict[str, str]] = production_assets.get("storyboard_panels", [])
        
        for idx, panel in enumerate(storyboard_panels, 1):
            scene_id = panel.get("scene_id", "UNKNOWN")
            imagen_prompt = panel.get("imagen_prompt", "")
            camera_angle = panel.get("camera_angle", "")
            
            with st.container(border=True):
                # Display scene ID as a header
                st.markdown(f"**Scene: {scene_id}**")
                
                # Display camera angle as a subtitle
                st.caption(f"📹 {camera_angle}")
                
                # Display the Imagen prompt in a code block for clarity
                st.markdown("**Imagen 3 Prompt:**")
                st.code(imagen_prompt, language="text")
    
    st.divider()
    
    # ========== Summary Stats ==========
    st.subheader("📊 Asset Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Pacing Points", len(pacing_curve))
    with summary_col2:
        st.metric("TTS Lines", len(tts_script))
    with summary_col3:
        st.metric("Storyboard Scenes", len(storyboard_panels))
    with summary_col4:
        total_words = sum(len(line.get("text", "").split()) for line in tts_script)
        st.metric("Script Word Count", total_words)
