# ADR 0010: Multimodal Media Ingestion via yt-dlp and Google GenAI File API

## Status
Accepted

## Context
MediaDNA previously required manual transcript entry. To deliver on the Agentic Cinema Hackathon's multimodal value proposition, the Deconstructor agent must extract pacing, audio cues, and emotional shifts directly from raw media (YouTube videos and local uploads).

## Decision
1. **Extraction Strategy**: Ingest YouTube URLs and video files by extracting high-efficiency audio streams (`m4a`/`mp3`) using `yt-dlp`. Audio preserves speech, cadence, pacing, and emotional cues while consuming ~90% fewer tokens and network bandwidth than full 1080p video streams.
2. **Cloud Upload Protocol**: Use the Google GenAI SDK File API (`client.files.upload`) to stage media for Gemini 2.5 Flash / 1.5 Pro multimodal processing.
3. **Safety & Cost Guardrails**: Enforce a strict maximum media duration cap (10 minutes) to prevent runaway token usage and long request timeouts.
4. **Lifecycle Management**: Implement automatic deletion of local temporary files and remote Google GenAI staged files immediately after Beat Sheet generation.

## Consequences
- **Pros**: Zero manual transcript preparation required by users; extracts rich audio/acoustic cues for the Beat Sheet.
- **Cons**: Adds `yt-dlp` system dependency and introduces a short ingestion latency before LLM processing starts.