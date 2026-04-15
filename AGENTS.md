# uControl SQL assistant instructions for Codex

## Goal
Improve SQL generation for the uControl MariaDB schema by combining:
- MCP schema inspection
- MCP query execution
- retrieval from human-written schema notes
- retrieval from generated schema metadata

## Required behaviour

1. Never jump directly from a user question to SQL.
2. First identify the relevant tables and the best join path.
3. Prefer trusted joins in `rag/relationship_map.md`.
4. Prefer explicit identifiers such as `GUID`, `ID`, bridge tables, and relationship tables.
5. Use denormalised fields only when the relationship map explicitly marks them as fallback or heuristic.
6. If a heuristic join is used, label it internally as low confidence.
7. Always filter relationship tables by discriminator columns such as `PARENT_KIND` and `CHILD_KIND` when those columns exist.
8. Avoid `SELECT *` unless the user explicitly asks for all columns.
9. Use `LIMIT` for exploration queries.
10. Do not silently invent joins from display text when a relationship table exists.

## Retrieval requirements

Before proposing SQL, retrieve relevant chunks from:
- `rag/core_entities.md`
- `rag/relationship_map.md`
- `rag/query_patterns.md`
- `rag/sql_generation_policy.md`
- generated schema catalog, if available

## Internal planning format
Use this internal structure before writing SQL:

- User intent
- Candidate tables
- Trusted join path
- Fallback join path, if needed
- Required filters
- Join confidence: high, medium, or low

Then produce SQL.

## Output rules

For internal tool use, you may generate both the plan and the SQL.
For user-facing output, do not expose hidden planning unless explicitly requested.

## Anti-patterns

- Do not join on `NAME` because it looks plausible.
- Do not join on `RUNNING_ON` if a relationship table already solves the problem.
- Do not assume `NAME`, `HOSTNAME`, and `GUID` are interchangeable.
- Do not assume all `ASSET_*` tables need manual semantic documentation.

## Validation

When implementing in the repo:
- keep the RAG source files small and focused
- add tests or at least sample evaluation queries
- validate a few known good examples against expected join paths
