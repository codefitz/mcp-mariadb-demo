# mcp-mariadb-demo

Minimal learning repo for running a Python MCP server backed by MariaDB.

## What You Get

- A simple MCP server with 3 tools:
  - `ping_database`
  - `list_tables`
  - `run_readonly_query`
- Local MariaDB via Docker Compose
- External MariaDB configuration path
- Example MCP server config in `mcp.json`

## Prerequisites

- Python 3.10+ (use `python3.10` or `python3.11`, not macOS system Python 3.9)
- Docker + Docker Compose (for local DB mode)

## Initialise MariaDB

```SQL
CREATE DATABASE mcp_demo;
CREATE USER 'mcp_user'@'localhost' IDENTIFIED BY 'StrongLocalPassword123!';
GRANT ALL PRIVILEGES ON mcp_demo.* TO 'mcp_user'@'localhost';
FLUSH PRIVILEGES;
```

## Quickstart (Local Docker DB)

1. Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Start MariaDB locally:

```bash
docker compose up -d
```

3. Copy env template:

```bash
cp .env.example .env
```

4. Run the MCP server:

```bash
python src/server.py
```

## External MariaDB Mode

Set environment variables for your remote or existing MariaDB instance:

```bash
export MARIADB_HOST="your-db-host"
export MARIADB_PORT="3306"
export MARIADB_USER="your-user"
export MARIADB_PASSWORD="your-password"
export MARIADB_DATABASE="your-database"
export MARIADB_SSL_DISABLED="false"
python src/server.py
```

If your environment requires TLS CA/certs, update `src/server.py` to pass full SSL options to PyMySQL.

## Tool Behavior

- `ping_database`: validates DB connection and returns server version.
- `list_tables(schema=None)`: lists tables in configured DB/schema.
- `run_readonly_query(sql, limit=50)`: only allows read-only SQL prefixes (`SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`).

## Example Queries

Use your MCP client to invoke:

- `ping_database`
- `list_tables`
- `run_readonly_query` with:

```sql
SELECT id, name, email, tier FROM customers ORDER BY id;
```

## MCP Client Configuration

Use `mcp.json` as a template. Point your MCP-capable client to this server command:

- command: `python`
- args: `src/server.py`
- cwd: project root

## Troubleshooting

- Port conflict on `3307`: change host port mapping in `docker-compose.yml` and update `MARIADB_PORT`.
- Access denied: verify username/password and DB grants.
- Connection timeout: check host firewall/security groups for external DB access.
- Table not found: local init SQL only runs on first container initialization. To reset:

```bash
docker compose down -v
docker compose up -d
```
