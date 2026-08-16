# ADR 0010-2: Multimodal File API Lifecycle Management

## Status
Accepted

## Context
Subtask F10.2 requires the `DeconstructorAgent` to process raw media (audio/video) alongside text prompts. The Google GenAI SDK supports this via the `client.files` API. However, uploading large media files introduces asynchronous processing states and stateful remote storage. If files are not explicitly deleted, they consume storage quotas (risk of hackathon credit exhaustion) and pose a data privacy risk for enterprise media assets.

## Decision
We will implement a **Strict Zero-Retention Lifecycle** within the `DeconstructorAgent` using the following architectural constraints:
1. **Asynchronous Polling**: After `client.files.upload()` is called, the agent must poll `client.files.get()` until the file state transitions from `PROCESSING` to `ACTIVE` (or `FAILED`).
2. **Deterministic Cleanup**: The LLM inference call (`client.aio.models.generate_content`) must be wrapped in a `try...finally` block. 
3. **Remote Deletion**: The `finally` block must execute `client.files.delete(name=file.name)` unconditionally, ensuring remote assets are purged regardless of successful schema validation, Pydantic errors, or network timeouts.

## Consequences
- **Positive**: Complete cost control; no storage bloat. Enterprise-grade security for user-uploaded media.
- **Negative**: Adds 2-10 seconds of latency to the API route due to the active polling phase before inference can begin.
- **Mitigation**: We mitigate latency by relying on F10.1's decision to only upload lightweight audio (`.m4a`) or low-res video, drastically reducing the Google backend processing time.