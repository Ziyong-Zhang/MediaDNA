from typing import Any

import requests
import streamlit as st

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

# Connection testing section
st.header("Backend Connection Test")

def ping_backend(url: str) -> dict[str, Any]:
    """Ping the backend health endpoint and return connection status and details.

    Args:
        url: The URL of the health check endpoint.

    Returns:
        A dictionary containing the success status and response data or error details.
    """
    try:
        response: requests.Response = requests.get(url, timeout=5.0)
        if response.status_code == 200:
            data: dict[str, Any] = response.json()
            return {"success": True, "data": data}
        return {"success": False, "error": f"HTTP status code {response.status_code}"}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}

# Button to trigger backend ping
if st.button("Test Connection"):
    backend_url: str = "http://localhost:8000/health"
    st.write(f"Pinging health endpoint: `{backend_url}`...")
    
    result: dict[str, Any] = ping_backend(backend_url)
    
    if result["success"]:
        st.success("Successfully connected to the backend!")
        st.json(result["data"])
    else:
        st.error(f"Failed to connect to the backend. Error: {result['error']}")
