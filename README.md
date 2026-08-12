# MediaDNA (MediaMirror AI)

MediaDNA is an AI-powered cinematic engine designed for the Agentic Cinema Hackathon. It extracts the "Viral DNA" from reference media and transforms it into actionable production assets, enabling creators to deconstruct successful content and reconstruct it with their unique vision.

## 🧬 Core Value

Extracting "Viral DNA" from reference media and generating actionable production assets. MediaDNA allows users to:
- **Deconstruct**: Analyze reference videos/scripts into structured JSON Beat Sheets.
- **Map**: Align creative intent with proven structural patterns.
- **Produce**: Generate high-fidelity assets including TTS audio and Imagen 3 prompts.

## 🏗 Architecture Stack

MediaDNA follows a strictly decoupled architecture:

- **Frontend**: [Streamlit](https://streamlit.io/) — Interactive UI for content creators.
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn — High-performance API orchestration.
- **Agent Layer**: [Google Cloud Agent Engines](https://cloud.google.com/products/agent-engine) / Native ADK — Multi-agent topology powered by Gemini.
- **Data Layer**: [ClickHouse Cloud](https://clickhouse.com/cloud) — Real-time analytics and storage, interfaced via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## 🚀 Quick Start

Ensure you have [uv](https://github.com/astral-sh/uv) and [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed.

### 1. Setup Environment
```bash
make setup
```

### 2. Authenticate with Google Cloud
```bash
make auth
```

### 3. Validate Installation
```bash
make check
```

## 📜 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Feature Roadmap](docs/features.md)
- [Decision Records](docs/adr/)

## ⚖️ License

MIT
