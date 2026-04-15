# uControl MCP + Schema RAG starter pack

This is a Codex-ready starter pack for improving SQL generation against the uControl MariaDB schema.

The goal is not to document all 500+ `ASSET_*` tables by hand. The goal is to:

1. Keep a small human-written semantic layer for important tables and trusted joins.
2. Keep a generated structural layer for broad schema awareness.
3. Force the model to reason about relationships before writing SQL.
4. Prefer trusted joins over denormalised or text-derived shortcuts.

OpenAI Codex can be guided by `AGENTS.md` files in a repository, and Codex works best when given clear documentation and instructions for how to navigate the codebase and run checks. citeturn791152search0turn791152search1

## What is included

- `AGENTS.md` — Codex instructions for implementing the workflow in your repo.
- `prompts/system_prompt.md` — system prompt for your SQL assistant.
- `rag/core_entities.md` — core table meanings and important identifiers.
- `rag/relationship_map.md` — trusted and heuristic join paths.
- `rag/query_patterns.md` — canonical business query examples.
- `rag/sql_generation_policy.md` — hard rules for SQL generation.
- `scripts/export_schema_catalog.sql` — SQL to export broad schema metadata from MariaDB.
- `scripts/example_pipeline.md` — implementation outline for the retrieval and generation flow.

## Recommended architecture

Use three layers:

### 1. Live MCP tools
Use MCP for:
- listing databases and tables
- retrieving table schema
- executing read-only SQL

### 2. Human-written semantic RAG
Use the files in `rag/` for:
- table meaning
- trusted joins
- caveats
- canonical examples
- anti-patterns

### 3. Generated schema catalog
Generate a catalog from `INFORMATION_SCHEMA` for all tables so the model has broad structural awareness without hand-writing everything.

## Retrieval strategy

Do not embed one giant schema file.

Chunk by section:
- one chunk per entity
- one chunk per relationship
- one chunk per canonical query
- one chunk for policy rules

This makes retrieval targeted and keeps the model from ignoring the useful parts.

## Runtime flow

Do not allow:

`user question -> SQL`

Use this instead:

`user question -> relationship reasoning -> confidence -> SQL`

Required steps:

1. Retrieve the most relevant chunks from `rag/`.
2. Ask the model to identify candidate tables and join path first.
3. Require it to classify the join as `high`, `medium`, or `low` confidence.
4. Only then generate SQL.
5. Execute through MCP.
6. If execution fails, inspect schema again rather than guessing a new join.

## Minimal implementation steps

### Step 1
Load the `rag/` files into your vector store.

### Step 2
Generate and store a `schema_catalog.json` from the SQL in `scripts/export_schema_catalog.sql`.

### Step 3
At runtime, retrieve:
- top entity chunks
- top relationship chunks
- top example query chunks
- policy chunk

### Step 4
Pass retrieved chunks plus the system prompt from `prompts/system_prompt.md` into your model.

### Step 5
Force a two-part answer internally:
- relationship plan
- SQL

### Step 6
Suppress internal planning in the user-facing response. Return only the SQL or the query results.

## What to document by hand

Do document by hand:
- important business tables
- relationship tables
- known bridge tables
- denormalised fields that look like join shortcuts
- common business questions

Do not document by hand:
- every long-tail table
- every metadata column
- every import table unless it is actually queried

## Priority list for manual coverage

Start with:
- `ASSET_HOST`
- `ASSET_SOFTWAREINSTANCE`
- `ASSET_SOFTWAREINSTANCE_RELATIONSHIP`
- `ASSET_NETWORKINTERFACE`
- `UMAP_CI`
- `UMAP_ENVIRONMENT`

Then add whatever tables show up in real user questions.

## What good output looks like

A good internal planning step should identify:
- candidate tables
- trusted join path
- fallback path if needed
- join confidence
- filters required by relationship tables

A bad plan is one that jumps straight to `NAME` or `RUNNING_ON` without first checking a relationship table.

## Suggested repository layout

```text
repo/
  AGENTS.md
  prompts/
    system_prompt.md
  rag/
    core_entities.md
    relationship_map.md
    query_patterns.md
    sql_generation_policy.md
  scripts/
    export_schema_catalog.sql
    example_pipeline.md
  generated/
    schema_catalog.json
```

## Notes

- Treat `GUID` as the preferred cross-table identifier when the relationship map says so.
- Treat text-derived joins as a last resort.
- Mark heuristic joins in the internal plan so they can be audited later.
- Create SQL views for high-value business objects if you can. That will outperform prompt-only fixes.
