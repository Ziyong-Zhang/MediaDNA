# ADR 0010-3: Hybrid Multimodal API Seam (FastAPI & Streamlit)

## Status
Accepted

## Context
Subtask F10.3 requires wiring the Streamlit frontend to the FastAPI backend to trigger the newly built multimodal `DeconstructorAgent`. To satisfy the hackathon's "Direct Your AI Crew" requirement and build a compelling Demo Video, users must be able to test their own raw media assets alongside public YouTube links.

## Decision
We will implement a **Hybrid Multipart Mode** payload architecture:
1. **Frontend (Streamlit)**: We will utilize `st.tabs` to offer two distinct input methods: "YouTube URL" (`st.text_input`) and "Upload File" (`st.file_uploader`). 
2. **API Client (`requests`)**: The frontend `api_client.deconstruct` function will dynamically switch to sending a `multipart/form-data` payload (using `files=` and `data=` kwargs in the `requests` library) to support raw binary transmission.
3. **Backend (FastAPI)**: The `/api/v1/deconstruct` endpoint will be refactored from accepting a strict Pydantic JSON body to accepting FastAPI `Form(...)` and `File(...)` dependencies.
4. **Processing Pipeline**: FastAPI will temporarily save the uploaded file via `media_service.save_uploaded_file`, pass the path to the Agent, and strictly clean it up in a `finally` block.

## Consequences
- **Positive**: Massive "Wow" factor for the hackathon demo. Complete flexibility for creators.
- **Negative**: Breaks the existing JSON-only contract for the `/api/v1/deconstruct` endpoint, requiring a slight update to `tests/test_backend.py` and `tests/test_frontend_api_client.py`.