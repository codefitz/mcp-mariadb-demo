# SQL generation policy

## Rules

1. Prefer explicit key joins over text matching.
2. Prefer relationship tables over denormalised helper columns.
3. Prefer `GUID` for cross-table joins when the relationship map says it is the stable key.
4. Always constrain relationship tables by discriminator fields such as `PARENT_KIND` and `CHILD_KIND` when relevant.
5. Use heuristic joins only when no trusted path exists.
6. If a heuristic join is used, classify it internally as low confidence.
7. Avoid `SELECT *` unless the user asks for all columns.
8. Use `LIMIT` for discovery queries.
9. Generate read-only SQL only.
10. Never fabricate tables or columns.

## Anti-patterns

- Do not join `ASSET_HOST.NAME` to `ASSET_SOFTWAREINSTANCE.RUNNING_ON` unless explicitly allowed.
- Do not infer network-interface ownership from display text if a bridge table exists.
- Do not assume `NAME`, `HOSTNAME`, and `GUID` are interchangeable.
- Do not treat all `ASSET_*` tables as equally important.

## Confidence rules

### High confidence
Use when:
- a documented relationship table or explicit join key exists
- join path matches both schema notes and live schema

### Medium confidence
Use when:
- the path uses a denormalised helper column documented as fallback

### Low confidence
Use when:
- the path depends on text parsing, display names, or assumed conventions
