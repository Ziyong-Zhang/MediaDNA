# ADR 0007: ClickHouse Data Modeling

## Status
Accepted

## Context
The MCP (Model Context Protocol) server requires a live ClickHouse database schema to fetch viral patterns for the Architect agent. We are targeting the "Creator Economy / YouTube / Streaming Media Blockbuster" segment of the hackathon. We need to define a consistent database schema for these viral templates, align it with our Pydantic schemas, and implement an automated schema migration/initialization script alongside a Python data seeder.

## Decision
We will define a lightweight SQL table creation script and a Python data seeder.

The `viral_templates` ClickHouse table will map exactly to the `ViralTemplate` Pydantic model:
- `pattern_id` String (primary key / order key)
- `pattern_type` String
- `description` String
- `source_ref` String

The ClickHouse table will be defined using the `MergeTree` engine, ordered by `pattern_id`.

```sql
CREATE TABLE IF NOT EXISTS viral_templates (
    pattern_id String,
    pattern_type String,
    description String,
    source_ref String
) ENGINE = MergeTree()
ORDER BY pattern_id;
```

We will implement:
1. `backend/db/init_db.py` to run the initialization.
2. `backend/db/seed.py` to seed three high-quality pacing structures.

## Consequences
- **Pros**:
  - Exact alignment between storage schemas and the application validation layer (Pydantic).
  - Explicit and repeatable database schema management.
- **Cons**:
  - Simple table recreation / modification is not fully managed by a heavy-weight migration framework (like Alembic), but this matches the agile hackathon scope.
