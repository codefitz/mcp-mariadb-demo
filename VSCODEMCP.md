What you need in VS Code

You need:
1.	VS Code
2.	GitHub Copilot / Chat enabled
3.	Your local MariaDB MCP server folder
4.	An mcp.json file telling VS Code how to start that server
5.	Then use Chat / Agent mode to call the tools exposed by the server  ￼

⸻

Step 1. Confirm the MCP server works outside VS Code

You already did this with Inspector, which is perfect. That proves:
- MariaDB is reachable
- .env is correct
- the MCP server starts
- the tools are exposed

So do not change the server code yet.

⸻

Step 2. Open the folder you want to work in

In VS Code, open either:
- your mariadb-mcp folder itself, or
- another project folder where you want the server available

For a first test, I’d open the mariadb-mcp folder directly. Fewer moving parts.

⸻

Step 3. Create the VS Code MCP config

VS Code stores MCP server definitions in an mcp.json file, either:
- in your workspace at .vscode/mcp.json, or
- in your user profile for all workspaces  ￼

For a first pass, use a workspace config.

In your terminal:

```shell
mkdir -p .vscode
vi .vscode/mcp.json
```

Paste this and replace the path:

```json
{
  "servers": {
    "mariadb-local": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/your-username/path/to/mariadb-mcp",
        "run",
        "server.py"
      ],
      "envFile": "/Users/your-username/path/to/mariadb-mcp/.env"
    }
  }
}
```

VS Code’s MCP docs show this exact pattern: a servers object in mcp.json, with command and args for local servers. The config file lives in .vscode/mcp.json for workspace scope.  ￼

```

⸻

Step 4. Make sure the path is correct

This is where people usually step on the rake.

Check these two paths exist:

```bash
ls /Users/your-username/path/to/mariadb-mcp
ls /Users/your-username/path/to/mariadb-mcp/.env
```

Also check uv is available from your shell:

```bash
which uv
uv --version
```

If uv is not found, VS Code cannot start the server.

⸻

Step 5. Let VS Code detect the server

Now in VS Code:
1.	Open Command Palette with Cmd+Shift+P
2.	Run MCP: List Servers
3.	You should see mariadb-local
4.	Start or enable it if needed

VS Code supports adding and managing MCP servers through mcp.json, and MCP: List Servers is one of the built-in management commands.  ￼

If prompted to trust the server, approve it only after checking the config. VS Code explicitly warns that local MCP servers can run arbitrary code.  ￼

⸻

Step 6. Check the server log if it fails

If it doesn’t appear, or shows an error:
1.	Cmd+Shift+P
2.	Run MCP: List Servers
3.	Select mariadb-local
4.	Choose Show Output

VS Code provides MCP output logs through the command palette and the chat error indicator.  ￼

Typical causes:
- wrong folder path
- wrong .env path
- uv not installed
- MariaDB not running
- broken JSON in mcp.json

⸻

Step 7. Open Chat in VS Code

Once the server is running:
1.	Open the Chat view
2.	Switch to Agent mode if needed
3.	Use prompts that require tools

VS Code agents can use MCP servers as tools in chat.  ￼

Start with prompts like:

`List the available databases from the MariaDB MCP server.`

Then:

`Show me the tables in mcp_demo.`

Then:

`Describe the schema of the tickets table.`

Then:

`Run a query to show all open tickets ordered by ticket_id.`


⸻

Step 8. Good first prompts to test

Use these in order.

Test 1

`List all databases available through the MariaDB MCP server.`

Test 2

`Show me the tables in the mcp_demo database.`

Test 3

`Describe the schema for the tickets table.`

Test 4

Run this SQL against mcp_demo:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
ORDER BY ticket_id;
```

Test 5

Which user has opened the most tickets? Show the SQL and the result.

⸻

Step 9. If tools exist but aren’t being used

In the chat input, use the Configure Tools button and make sure the MCP server tools are enabled. VS Code exposes available MCP tools there and lets you toggle them on or off.  ￼

If the model answers from thin air instead of querying the database, be more explicit:

Use the MariaDB MCP tools, not your general knowledge. List the tables in mcp_demo and then query the tickets table.

⸻

Step 10. Alternative: add the server through the UI

Instead of editing JSON manually, VS Code also supports:
- MCP: Add Server from the Command Palette
- or opening the user/workspace MCP config from commands  ￼

But for your case, hand-editing `mcp.json` is faster and clearer.

⸻

Step 11. A known-good `mcp.json` template

Use this exact shape:

```json
{
  "servers": {
    "mariadb-local": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mariadb-mcp",
        "run",
        "server.py"
      ],
      "envFile": "/ABSOLUTE/PATH/TO/mariadb-mcp/.env"
    }
  }
}
```

That is the bit that matters most.

⸻

Step 12. The shortest possible route

Do this:

```shell
cd /Users/your-username/path/to/mariadb-mcp
mkdir -p .vscode
vi .vscode/mcp.json
```

Paste:

```json
{
  "servers": {
    "mariadb-local": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/your-username/path/to/mariadb-mcp",
        "run",
        "server.py"
      ],
      "envFile": "/Users/your-username/path/to/mariadb-mcp/.env"
    }
  }
}
```

Then in VS Code:
- Cmd+Shift+P
- MCP: List Servers
- start mariadb-local
- open Chat
- ask: Show me the tables in mcp_demo
