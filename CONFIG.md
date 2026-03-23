# Config Guide

This file covers the practical setup for running the root demo and connecting MCP clients to it.

## Environment

The root server expects these variables in `.env`:

```dotenv
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_USER=mcp_user
MARIADB_PASSWORD=your_password
MARIADB_DATABASE=mcp_demo
MARIADB_SSL_DISABLED=true
```

`src/server.py` calls `load_dotenv()`, so the root `.env` is loaded automatically when you start the server from the repo root.

## Loading The Demo Data

Use the same connection details from `.env`:

```bash
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/001_schema.sql
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/002_data.sql
```

## Inspector

The fastest end-to-end check is MCP Inspector:

```bash
npx @modelcontextprotocol/inspector -- python src/server.py
```

Once it opens:

1. Run `ping_database`
2. Run `list_tables`
3. Run `run_readonly_query`

Good first query:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
ORDER BY ticket_id;
```

## Editor Config

The included [mcp.json](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo/mcp.json) is the simple template:

```json
{
  "mcpServers": {
    "mariadb-demo": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "."
    }
  }
}
```

For VS Code, Cursor, or similar tools, the important parts are:

- run `python src/server.py`
- use the repo root as `cwd`
- keep your actual DB settings in the root `.env`

If your client requires an absolute working directory, replace `.` with your repo path.

## Troubleshooting

Check these in order:

1. `.env` matches your actual MariaDB host, port, user, password, and database
2. the schema and seed files have been loaded
3. `python src/server.py` starts without import errors
4. the database is reachable directly with the `mariadb` CLI

Direct DB check:

```bash
mariadb -h <host> -P <port> -u <user> -p <database>
```

Then run:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM tickets;
```

If the server starts and then waits quietly, that is expected. It is waiting for an MCP client connection.
