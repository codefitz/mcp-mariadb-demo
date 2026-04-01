# mcp-mariadb-demo

Minimal learning repo for a Python MCP server backed by MariaDB.

This repo keeps one supported implementation:

- server: `src/server.py`
- seed SQL: `db/init/`
- generic MCP client template for non-VS Code clients: `mcp.json`
- AnythingLLM MCP template: `anythingllm_mcp_servers.json`
- VS Code workspace MCP config: `.vscode/mcp.json`
- config guide: `CONFIG.md`

The demo exposes three tools:

- `ping_database`
- `list_tables`
- `run_readonly_query`

Important:

- VS Code does not use the root `mcp.json` file.
- AnythingLLM does not use the root `mcp.json` file either.
- The root `anythingllm_mcp_servers.json` is a template to copy into AnythingLLM's `plugins/` storage directory.
- The root `mcp.json` is only a generic template for other MCP clients that expect a top-level `mcpServers` object.
- VS Code uses `.vscode/mcp.json`.

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

If you are using `uv`, sync the project dependencies from `pyproject.toml`:

```bash
uv sync
```

Then run the server with:

```bash
uv run src/server.py
```

or

```
uv run src/server.py --transport http --host 127.0.0.1 --port 8000 --path /mcp
```

If you are using plain `venv` + `pip`, keep the environment named `.venv` if you also want `uv` commands to pick it up automatically. A separate `venv/` directory will not be used by `uv run` unless you activate it first.

Otherwise, the standard `venv` flow still works:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. If you need a local MariaDB on Ubuntu or Debian, install it first.

For a local server plus the `mariadb` CLI:

```bash
sudo apt update
sudo apt install -y mariadb-server mariadb-client
sudo systemctl enable --now mariadb
```

Create the demo database and user expected by `.env.example`:

```bash
sudo mariadb
```

```sql
CREATE DATABASE mcp_demo;
CREATE USER 'mcp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON mcp_demo.* TO 'mcp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

If you are connecting to an existing remote MariaDB instead, `sudo apt install -y mariadb-client` is enough.

3. Create `.env` from the template and point it at your MariaDB instance.

```bash
cp .env.example .env
```

4. Load the demo schema and data.

```bash
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/001_schema.sql
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/002_data.sql
```

5. Run the server.

```bash
python src/server.py
```

Or with `uv`:

```bash
uv run src/server.py
```

If it appears idle, that is normal. In stdio mode it is waiting for an MCP client.

If you want to run the MCP server on a separate machine and connect to it from VS Code over the network, see `CONFIG.md`.

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
- `src/server.py` supports `--transport stdio`, `--transport streamable-http`, and `--transport sse`. `--transport http` is accepted as an alias for `streamable-http`.
- `run_readonly_query` only allows SQL starting with `SELECT`, `SHOW`, `DESCRIBE`, or `EXPLAIN`.
- `docker-compose.yml` is still available if you want a disposable local MariaDB, but it is optional.
- `mariadb-mcp/` is a scratch reference clone and is ignored by git; it is not part of the active demo.

For client setup, VS Code chat setup, and troubleshooting, see `CONFIG.md`.
