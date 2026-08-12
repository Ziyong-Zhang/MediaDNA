# ADR 0003: Deconstructor Agent Schema with Pydantic v2

## Status
Proposed

## Context
The "MediaDNA" project requires transforming unstructured reference media (such as transcripts, scripts, audio, and video) into a structured analysis. This structured representation, called a "Beat Sheet," must be stored in ClickHouse and consumed by other agents (Architect, Director) in a consistent format. 
We need to define a robust, strictly typed data contract between the LLM output and our system services.

## Decision
We decide to use Pydantic v2 to define the `BeatSheet` model. 
When interacting with Gemini 1.5 Pro via the Native GCP ADK, we will leverage structured JSON output matching this schema. Pydantic v2 provides excellent performance, built-in validation, and native JSON schema generation which can be passed directly to or enforced alongside the Gemini API.

## Schema Specification
The schema will contain:
- `hook_analysis` (string): Description and analysis of the opening hook.
- `pacing_curve` (list of strings): The pacing profile/structure (e.g., ["fast", "slow build", "climax"]).
- `key_events` (list of dicts): Chronological timeline of events, where each event has a `timestamp` (string) and `event_description` (string).

## Consequences
- **Type Safety**: Mypy --strict can fully type check all references to the `BeatSheet` model.
- **Interoperability**: The resulting structured JSON is directly compatible with downstream agent systems and ClickHouse schema parsing.
- **Integration with Vertex AI**: Ensures that prompt engineering can rely on explicit JSON schemas for responses.
