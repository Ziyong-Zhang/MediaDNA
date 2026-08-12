# MediaDNA Architecture

This document details the multi-agent topology and system architecture of MediaDNA.

## 🌐 System Overview

MediaDNA is built on a strictly decoupled architecture where the UI (Streamlit) never directly touches the database. All operations are orchestrated through a FastAPI backend that manages communication with the Google Cloud Agent Engines.

## 🤖 Multi-Agent Topology

The intelligence of MediaDNA is distributed across three specialized agents, built using the Native GCP ADK:

### 1. The Deconstructor
- **Role**: Multimodal Analysis.
- **Function**: Parses input media (video, audio, text) and extracts structural elements.
- **Output**: JSON Beat Sheets containing pacing, tone, key events, and visual cues.

### 2. The Architect
- **Role**: Structural Alignment & Context Mapping.
- **Function**: Takes the deconstructed DNA and maps it against user-provided creative constraints.
- **Output**: A blueprint for the new production, ensuring structural integrity while allowing for creative deviation.

### 3. The Director
- **Role**: Asset Production.
- **Function**: Transforms the Architect's blueprint into tangible assets.
- **Output**: 
    - Text-to-Speech (TTS) scripts and audio generation.
    - High-fidelity Imagen 3 visual prompts.
    - Production metadata.

## 🔌 Data Layer & MCP

The data layer in MediaDNA is strictly isolated. 

**Critical Requirement**: All database interactions with **ClickHouse Cloud** MUST be routed through the **Model Context Protocol (MCP)**. 

- This ensures that agents can interact with the data layer using a standardized, tool-based interface.
- Prevents hardcoding database credentials or complex ORM logic within the agent definitions.
- Facilitates real-time analytics on media patterns and viral trends.

## 🛡 Security & Authentication

- **Identity**: Google Cloud Identity & Access Management (IAM).
- **Authentication**: Application Default Credentials (ADC).
- **Inter-service**: Internal API tokens between Streamlit and FastAPI.
