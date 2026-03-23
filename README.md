# mcp-mariadb-demo

Minimal learning repo for a Python MCP server backed by MariaDB.

This repo keeps one supported implementation:

- server: `src/server.py`
- seed SQL: `db/init/`
- client template: `mcp.json`
- config guide: `CONFIG.md`

The demo exposes three tools:

- `ping_database`
- `list_tables`
- `run_readonly_query`

## Scope

This repo is meant to teach:

- how a small MCP server is structured
- how to load MariaDB connection settings from `.env`
- how an MCP client connects over stdio
- how to keep a simple query tool read-only

It does not try to cover packaging, auth, vector search, or production deployment.

## Demo Data

The seed SQL creates a small IT/helpdesk dataset with:

- `users`
- `assets`
- `tickets`
- `knowledge_articles`

## Quickstart

1. Create a virtual environment and install dependencies.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Create `.env` from the template and point it at your MariaDB instance.

```bash
cp .env.example .env
```

3. Load the demo schema and data.

```bash
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/001_schema.sql
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/002_data.sql
```

4. Run the server.

```bash
python src/server.py
```

If it appears idle, that is normal. In stdio mode it is waiting for an MCP client.

## Verify The Database

Connect directly and check the seeded tables:

```bash
mariadb -h <host> -P <port> -u <user> -p <database>
```

```sql
SHOW TABLES;
SELECT ticket_id, title, priority, status FROM tickets ORDER BY ticket_id;
```

## Example Queries

Use your MCP client to call `run_readonly_query` with:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
ORDER BY ticket_id;
```

```sql
SELECT u.full_name, a.asset_tag, a.model
FROM assets a
LEFT JOIN users u ON a.assigned_user_id = u.user_id
ORDER BY a.asset_tag;
```

## Notes

- `src/server.py` loads the root `.env` automatically.
- `run_readonly_query` only allows SQL starting with `SELECT`, `SHOW`, `DESCRIBE`, or `EXPLAIN`.
- `docker-compose.yml` is still available if you want a disposable local MariaDB, but it is optional.
- `mariadb-mcp/` is a scratch reference clone and is ignored by git; it is not part of the active demo.

For client setup and troubleshooting, see `CONFIG.md`.
