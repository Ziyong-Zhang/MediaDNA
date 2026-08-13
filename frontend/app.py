import streamlit as st

from frontend import api_client
from frontend.api_client import BackendError

# Configure page layout
st.set_page_config(
    page_title="MediaDNA: Viral Structure Extractor",
    layout="wide",
)

# Render main header
st.title("MediaDNA: Viral Structure Extractor")

# Sidebar for Agent Modes
st.sidebar.title("Agent Modes")
st.sidebar.markdown("Select an agent mode below to inspect or run.")
agent_mode: str = st.sidebar.selectbox(
    "Active Agent",
    options=["Deconstructor", "Architect", "Director"],
    index=0,
)
st.sidebar.info(f"Currently selected agent: {agent_mode}")

# Reference Media Input Placeholders
st.header("1. Deconstructor: Reference Media Inputs")
media_type: str = st.radio(
    "Select Input Type",
    options=["File Upload", "Text Transcript/Script"],
    horizontal=True,
)

transcript_text: str = ""
if media_type == "File Upload":
    uploaded_file = st.file_uploader(
        "Upload reference media file (video, audio, etc.)",
        type=["mp4", "mp3", "wav", "m4a"],
    )
    if uploaded_file is not None:
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        st.warning("File-based deconstruction is not yet wired to the backend; use a text transcript instead.")
else:
    transcript_text = st.text_area(
        "Enter reference transcript or script content",
        height=200,
        placeholder="Paste your video/audio transcript or creative script here...",
    )
    if transcript_text:
        st.info(f"Transcript input received ({len(transcript_text)} characters).")

if st.button("Run Deconstructor", disabled=not transcript_text):
    try:
        beat_sheet = api_client.deconstruct(transcript_text)
    except BackendError as e:
        st.error(f"Deconstructor call failed: {e}")
    else:
        st.session_state["beat_sheet"] = beat_sheet

if "beat_sheet" in st.session_state:
    st.subheader("Beat Sheet")
    st.json(st.session_state["beat_sheet"])

# Architect workflow: only available once a Beat Sheet exists
if "beat_sheet" in st.session_state:
    st.header("2. Architect: Structural Alignment")
    creative_brief: str = st.text_area(
        "Describe your creative brief / constraints for the new production",
        height=120,
        placeholder="e.g. Adapt this for a cooking channel with a twist ending...",
    )
    if st.button("Run Architect", disabled=not creative_brief):
        try:
            blueprint = api_client.architect(st.session_state["beat_sheet"], creative_brief)
        except BackendError as e:
            st.error(f"Architect call failed: {e}")
        else:
            st.session_state["blueprint"] = blueprint

    if "blueprint" in st.session_state:
        st.subheader("Blueprint")
        st.json(st.session_state["blueprint"])

# Director workflow: only available once a Blueprint exists
if "blueprint" in st.session_state:
    st.header("3. Director: Asset Production")
    if st.button("Run Director"):
        try:
            production_assets = api_client.produce(st.session_state["blueprint"])
        except BackendError as e:
            st.error(f"Director call failed: {e}")
        else:
            st.session_state["production_assets"] = production_assets

    if "production_assets" in st.session_state:
        assets = st.session_state["production_assets"]
        st.subheader("TTS Script")
        st.table(assets["tts_script"])
        st.subheader("Visual Prompts")
        st.table(assets["visual_prompts"])
        st.subheader("Metadata")
        st.json(assets["metadata"])

# Connection testing section
st.header("Backend Connection Test")

# Button to trigger backend ping
if st.button("Test Connection"):
    st.write(f"Pinging health endpoint: `{api_client.BACKEND_URL}/health`...")
    try:
        health_data = api_client.health()
    except BackendError as e:
        st.error(f"Failed to connect to the backend. Error: {e}")
    else:
        st.success("Successfully connected to the backend!")
        st.json(health_data)

