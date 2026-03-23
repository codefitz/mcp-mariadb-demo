The simplest way forward is this:

Fastest route: use MCP Inspector first

This is the easiest way to prove the server works before involving Cursor or Claude Desktop. The official MCP Inspector is specifically for testing and debugging MCP servers, including exploring and executing tools.  ￼

1. Keep your MariaDB MCP server folder ready

You should already be in your mariadb-mcp folder with:
- `.env`
- dependencies installed
- your demo DB running locally

2. Start the Inspector against your server

From the `mariadb-mcp` folder, run:

```shell
npx @modelcontextprotocol/inspector -- uv run server.py
```

The Inspector docs and repo show this pattern: use `npx @modelcontextprotocol/inspector`, then pass the server command after `--`.  ￼

If npx is missing, install Node first:

```shell
brew install node
```

3. Open the Inspector UI

It should open a local browser UI, typically on port 6274. The Inspector repo documents that the UI runs on port 6274 by default.  ￼

4. In the Inspector, go to Tools

You should see MariaDB tools exposed by the MCP server. The MariaDB MCP server provides tools for database management and querying, including standard SQL operations.  ￼

5. Run tools in this order

Start with discovery, then query:

A. list databases
You want to confirm your mcp_demo database is visible.

B. list tables for mcp_demo
You should see:
- users
- assets
- tickets
- knowledge_articles

C. describe schema for tickets

D. execute query with something simple, for example:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
ORDER BY ticket_id;
```

Then try:

```sql
SELECT u.full_name, a.asset_tag, a.model
FROM assets a
JOIN users u ON a.assigned_user_id = u.user_id
ORDER BY u.full_name;
```

And:

```sql
SELECT title, category
FROM knowledge_articles
ORDER BY created_at DESC;
```

That gets you from “server exists” to “I am actually querying the demo DB”.

⸻

What is happening under the hood

The flow is:

MariaDB database
→ MariaDB MCP server
→ MCP client
→ you ask for tables / schemas / SQL results

So if you just run:

```shell
uv run server.py
```

it often looks like “nothing is happening”. That is normal. In stdio mode, it is waiting for an MCP client to connect and send tool requests. The MariaDB MCP README documents uv run server.py as the stdio transport for client integration.  ￼

[VSCode Setup](VSCODEMCP.md)

⸻

If you want to use Claude Desktop instead

The official MCP docs use Claude Desktop as the example local MCP client, and Anthropic’s support docs say you can view connected MCP servers and their tools from the app.  ￼

Put a config like this in Claude Desktop’s MCP config:

```json
{
  "mcpServers": {
    "MariaDB_Server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/mariadb-mcp",
        "run",
        "server.py"
      ],
      "envFile": "/Users/yourname/path/to/mariadb-mcp/.env"
    }
  }
}
```

Then restart Claude Desktop. Once connected, ask things like:
- “List the tables in mcp_demo”
- “Show me the schema for tickets”
- “Run: SELECT * FROM users”
- “Which tickets are still open?”

The local-server connection pattern for Claude Desktop is documented in the MCP docs, and Claude support notes that connected MCP servers and their tools appear in the Connectors or Developer settings area.  ￼

⸻

If you want to use Cursor instead

Cursor has MCP support and documents configuration through MCP settings and mcp.json.  ￼

A typical config is the same idea:

```json
{
  "mcpServers": {
    "MariaDB_Server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/mariadb-mcp",
        "run",
        "server.py"
      ],
      "envFile": "/Users/yourname/path/to/mariadb-mcp/.env"
    }
  }
}
```

Then restart Cursor and ask the agent:
- “List all tables in mcp_demo”
- “Show me all open tickets”
- “Which user has the most tickets?”

⸻

Quick sanity checks if it does not work

Run these locally first:

Can MariaDB itself be queried?

```shell
mariadb -u mcp_user -p mcp_demo
```

Then:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM tickets;
```

Is the `.env` correct?

Check:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=mcp_user
DB_PASSWORD=StrongLocalPassword123!
DB_NAME=mcp_demo
MCP_READ_ONLY=true
```

Does the server start without crashing?

```shell
cd /Users/yourname/path/to/mariadb-mcp
uv run server.py
```

If it just sits there quietly, that usually means the stdio server is waiting for a client, not that it is broken. The stdio transport is meant for client connection, not direct terminal interaction.  ￼

⸻

Do this now:

```shell
cd /Users/yourname/path/to/mariadb-mcp
npx @modelcontextprotocol/inspector -- uv run server.py
```

Then in the Inspector:
1.	open Tools
2.	find the MariaDB tools
3.	list databases
4.	list tables in mcp_demo
5.	run a simple SELECT
