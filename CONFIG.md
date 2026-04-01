# Config Guide

This file is the practical setup guide for the demo. If you are new to MCP or VS Code chat, follow the steps in order.

## What You Need

Before you start, make sure you have:

- Python 3.11
- this repo checked out locally
- a MariaDB server you can connect to
- the `mariadb` CLI installed
- VS Code with Copilot Chat enabled if you want MCP tools in chat

## 1. Create `.env`

The root server reads database settings from the repo root `.env`.

Create it from the template:

```bash
cp .env.example .env
```

The expected values are:

```dotenv
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_USER=mcp_user
MARIADB_PASSWORD=your_password
MARIADB_DATABASE=mcp_demo
MARIADB_SSL_DISABLED=true
```

`src/server.py` calls `load_dotenv()`, so you do not need to export these variables manually when starting the server from the repo root.

## 2. If Needed, Install MariaDB On Ubuntu Or Debian

If you already have a MariaDB server and know its connection details, skip to the next section.

If you want a local MariaDB server on Ubuntu or Debian:

```bash
sudo apt update
sudo apt install -y mariadb-server mariadb-client
sudo systemctl enable --now mariadb
```

Create the demo database and user that match `.env.example`:

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

If you are connecting to a remote MariaDB instead of running one locally, install just the client:

```bash
sudo apt install -y mariadb-client
```

## 3. Load The Demo Schema And Data

Use the same connection details you put in `.env`:

```bash
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/001_schema.sql
mariadb -h <host> -P <port> -u <user> -p <database> < db/init/002_data.sql
```

Example for the local Ubuntu setup above:

```bash
mariadb -h localhost -P 3306 -u mcp_user -p mcp_demo < db/init/001_schema.sql
mariadb -h localhost -P 3306 -u mcp_user -p mcp_demo < db/init/002_data.sql
```

## 4. Verify The Database Works

Before involving MCP or VS Code, confirm the database is reachable:

```bash
mariadb -h <host> -P <port> -u <user> -p <database>
```

Then run:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM tickets;
EXIT;
```

If this fails, fix the database connection first. VS Code chat will not work until this works.

## 5. Verify The MCP Server Works Outside VS Code

Create the virtual environment and install dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Now start the MCP server once from the terminal:

```bash
python src/server.py
```

If it appears to do nothing, that is normal. In stdio mode it is waiting for an MCP client.

Press `Ctrl+C` to stop it after you confirm it starts without errors.

Optional but useful: test with MCP Inspector.

```bash
npx @modelcontextprotocol/inspector -- python src/server.py
```

In Inspector, run:

1. `ping_database`
2. `list_tables`
3. `run_readonly_query`

Good first query:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
ORDER BY ticket_id;
```

If the server does not start here, do not move on to VS Code yet.

## 6. Stop A Running MCP Server

How you stop it depends on how it was started.

If you started it manually in a terminal with:

```bash
python src/server.py
```

stop it with:

- `Ctrl+C`

If VS Code started it from `.vscode/mcp.json`:

1. Open the Command Palette.
2. Run `MCP: List Servers`.
3. Select `mariadbDemo`.
4. Choose `Stop`.

If you are not sure where it is running from, first try `Ctrl+C` in the terminal where you started it. If that is not the running copy, stop it from `MCP: List Servers` in VS Code.

## 7. Verify You Are Connected To The Remote MariaDB

This matters when your local MariaDB contains the same demo data as the remote one.

### Step 7.1 Check `.env` First

Open `.env` and confirm these values point at the remote database, not your local one:

- `MARIADB_HOST`
- `MARIADB_PORT`
- `MARIADB_USER`
- `MARIADB_DATABASE`

If `MARIADB_HOST` is `localhost` or `127.0.0.1`, you are pointing at the local machine, not a remote database.

### Step 7.2 Verify With A Read-Only Query

The most useful check is to ask the MCP server for MariaDB server metadata instead of demo rows.

Use `run_readonly_query` with:

```sql
SELECT
  DATABASE() AS database_name,
  CURRENT_USER() AS current_user,
  @@hostname AS server_hostname,
  @@port AS server_port,
  VERSION() AS server_version;
```

You can run that:

- in MCP Inspector
- from VS Code chat by asking it to use `run_readonly_query`
- from any MCP client connected to this server

### Step 7.3 How To Read The Result

Check these fields:

- `database_name`: should be the database you expect, for example `mcp_demo`
- `current_user`: should be the MariaDB user you expect for the remote server
- `server_port`: should match the remote MariaDB port you configured
- `server_hostname`: should identify the MariaDB server you actually reached

Important: `server_hostname` might be the remote server's internal machine name, not the same DNS name you put in `MARIADB_HOST`. That is normal. The important part is that it should not look like your local machine or `localhost` when you expect a remote server.

### Step 7.4 Compare Against The Local MariaDB If Needed

If you still are not sure, connect directly to your local MariaDB and run the same query there:

```bash
mariadb -h localhost -P 3306 -u mcp_user -p mcp_demo
```

```sql
SELECT
  DATABASE() AS database_name,
  CURRENT_USER() AS current_user,
  @@hostname AS server_hostname,
  @@port AS server_port,
  VERSION() AS server_version;
```

If the local and MCP results show different `server_hostname`, `current_user`, or `server_port`, then the MCP server is not connected to the local MariaDB.

### Step 7.5 Good VS Code Chat Prompt

In VS Code chat, use a prompt like:

- `Use the MariaDB MCP tools and run a read-only query to show DATABASE(), CURRENT_USER(), @@hostname, @@port, and VERSION().`

That forces the model to ask the MCP server for connection metadata instead of answering from the demo data.

## 8. Run The MCP Server On A Separate Host

This section is for the architecture where you have:

- one machine running MariaDB
- a different machine running the MCP server
- your laptop running VS Code chat

That setup is supported, but not with local `stdio` from VS Code. For a separate MCP host, run this server over streamable HTTP or SSE and have VS Code connect to the remote URL.

### Step 8.1 What Runs Where

In this architecture:

- the DB server hosts MariaDB
- the MCP server machine runs this repo's `src/server.py`
- your laptop runs VS Code and connects to the MCP server over the network

The `.env` file belongs on the MCP server machine, because that machine is the one opening the MariaDB connection.

### Step 8.2 Prepare The MCP Server Machine

On the MCP server host:

1. Check out this repo.
2. Create `.env` with the MariaDB server's host, port, user, password, and database.
3. Create the virtual environment and install dependencies.

Commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` so `MARIADB_HOST` points at the database server, not the MCP host itself.

### Step 8.3 Start The MCP Server In Streamable HTTP Mode

On the MCP server host, run:

```bash
python src/server.py --transport streamable-http --host 0.0.0.0 --port 8000 --path /mcp
```

What this does:

- `--transport streamable-http`: runs the MCP server over HTTP instead of local stdio
- `--host 0.0.0.0`: listens on the MCP server machine's network interfaces
- `--port 8000`: exposes the service on port 8000
- `--path /mcp`: serves the MCP endpoint at `/mcp`

If you prefer, `--transport http` is accepted as a shortcut and maps to `streamable-http`.

If you prefer SSE, you can use:

```bash
python src/server.py --transport sse --host 0.0.0.0 --port 8000 --path /mcp
```

### Step 8.4 Make Sure Your Laptop Can Reach The MCP Host

From your laptop, you must be able to reach the MCP server host and port.

That usually means:

- the MCP host is on the same LAN, VPN, or Tailnet as your laptop
- port `8000` is open on the MCP host firewall
- you know the hostname or IP address of the MCP host

Example remote URL:

- `http://mcp-host.example.internal:8000/mcp`

### Step 8.5 Configure VS Code On Your Laptop

On your laptop, in the local copy of this repo, create `.vscode/mcp.json` like this:

```json
{
  "servers": {
    "mariadbDemoRemote": {
      "type": "http",
      "url": "http://mcp-host.example.internal:8000/mcp"
    }
  }
}
```

Replace the URL with the actual hostname or IP of the MCP server machine.

Important:

- in this remote-host setup, VS Code does not need the database credentials locally
- the DB credentials live on the MCP server host in that machine's `.env`
- your laptop only needs network access to the MCP server URL

### Step 8.6 Verify The Full Chain

From VS Code chat on your laptop, ask the remote MCP server to run:

```sql
SELECT
  DATABASE() AS database_name,
  CURRENT_USER() AS current_user,
  @@hostname AS server_hostname,
  @@port AS server_port,
  VERSION() AS server_version;
```

This verifies the full path:

- VS Code on your laptop is connected to the MCP server host
- the MCP server host is connected to the MariaDB server

### Step 8.7 Security Warning

This demo does not add authentication or TLS by itself.

For a private lab, LAN, VPN, or Tailnet setup, that may be fine.

Do not expose this demo server directly to the public internet without adding proper authentication and transport security first.

## 9. Set Up VS Code MCP Chat

This is the exact flow for a beginner.

### Important

VS Code does not use the root [mcp.json](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo/mcp.json) file in this repo.

For VS Code, you must create a separate file at `.vscode/mcp.json` inside this workspace, and that file must use a top-level `servers` object.

You do not need to run `python src/server.py` manually before using `MCP: List Servers`. VS Code can start the server itself from `.vscode/mcp.json`.

The easiest way to get this wrong is to open the wrong folder in VS Code.

If you open a parent folder such as `GitHub/` instead of this repo, VS Code may use a different `.vscode/mcp.json` from that parent folder. Then MCP can silently start the wrong server with the wrong `.env`.

For this demo, always open this exact folder as the workspace root:

- [mcp-mariadb-demo](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo)

### Step 9.1 Create `.vscode/mcp.json`

Create the folder and file:

```bash
mkdir -p .vscode
```

Then create `.vscode/mcp.json` with this exact content:

```json
{
  "servers": {
    "mariadbDemo": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/src/server.py"],
      "envFile": "${workspaceFolder}/.env"
    }
  }
}
```

What each line means:

- `servers`: the top-level key VS Code expects
- `mariadbDemo`: the name that will appear in `MCP: List Servers`
- `type: "stdio"`: VS Code should start the server as a local process
- `command`: use the Python interpreter from this repo's virtual environment
- `args`: run this repo's `src/server.py`
- `envFile`: load the same `.env` you already configured

If you are on Windows, change `command` to `${workspaceFolder}\\.venv\\Scripts\\python.exe`.

### Step 9.2 Open The Correct Folder In VS Code

In VS Code, open this repo folder as your workspace, not a parent folder that happens to contain it.

Do not open some other parent folder and expect `${workspaceFolder}` to point here.

- [mcp-mariadb-demo](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo)

Quick sanity check:

- in VS Code Explorer, you should see this repo's `src/`, `db/`, `.env`, and `.vscode/` at the top level
- `${workspaceFolder}` should mean `/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo`

### Step 9.3 List And Start The MCP Server

In VS Code:

1. Open the Command Palette.
2. Run `MCP: List Servers`.
3. You should see `mariadbDemo`.
4. Start it if it is not already running.
5. Approve the trust prompt after checking the config.

If `mariadbDemo` does not appear, the usual cause is that `.vscode/mcp.json` is missing or malformed.

### Step 9.4 Check Logs If Startup Fails

If the server is listed but will not start:

1. Run `MCP: List Servers`.
2. Select `mariadbDemo`.
3. Choose `Show Output`.

Check for these common mistakes:

- `.vscode/mcp.json` uses `mcpServers` instead of `servers`
- the JSON is invalid
- `${workspaceFolder}/.venv/bin/python` does not exist
- `.env` has the wrong database settings
- the database is not reachable

### Step 9.5 Use The Server In Chat

Once the server is running:

1. Open Chat in VS Code.
2. Switch to agent mode if needed.
3. Make sure the `mariadbDemo` tools are enabled in the tools/configure button.
4. Ask the model to use the MariaDB MCP tools.

Good first prompts:

- `Use the MariaDB MCP tools to list the tables in mcp_demo.`
- `Describe the schema of the tickets table.`
- `Run a read-only query to show all tickets ordered by ticket_id.`

If the model answers from memory instead of using tools, be explicit:

- `Use the MariaDB MCP tools, not general knowledge. First list the tables in mcp_demo, then query tickets.`

### Step 9.6 If VS Code Connects To The Wrong Database

If the server appears to work but is clearly connected to the wrong MariaDB, do this in order:

1. Open [.env](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo/.env) and confirm `MARIADB_HOST` points at the remote host you expect.
2. Make sure VS Code has [mcp-mariadb-demo](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo) open as the workspace root, not a parent folder.
3. Open [.vscode/mcp.json](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo/.vscode/mcp.json) and confirm it uses `${workspaceFolder}/src/server.py` and `${workspaceFolder}/.env`.
4. Run `MCP: List Servers`, select `mariadbDemo`, and choose `Stop`.
5. Run `MCP: Reset Cached Tools`.
6. Start `mariadbDemo` again from `MCP: List Servers`.
7. Rerun the metadata query from section 7:

```sql
SELECT
  DATABASE() AS database_name,
  CURRENT_USER() AS current_user,
  @@hostname AS server_hostname,
  @@port AS server_port,
  VERSION() AS server_version;
```

If you still see your local machine name, VS Code is still not using this workspace's `.vscode/mcp.json`.

## 10. Other MCP Clients

The root [mcp.json](/Users/fitzmoskal/Code/GitHub/mcp-mariadb-demo/mcp.json) is only a generic template for non-VS Code MCP clients that expect a top-level `mcpServers` object. It is not the file VS Code reads.

```json
{
  "mcpServers": {
    "mariadb-demo-template": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "."
    }
  }
}
```

The `mariadb-demo-template` name is deliberate so it is obvious this file is a starting point to copy or adapt, not the active VS Code workspace config.

For clients that support this format, the important parts are:

- run `python src/server.py`
- use the repo root as `cwd`
- keep your actual DB settings in the root `.env`

If your client requires an absolute working directory, replace `.` with your repo path.

## 11. AnythingLLM

AnythingLLM does not read the root [mcp.json](/Volumes/Hub/Code/GitHub/mcp-mariadb-demo/mcp.json). It expects a separate file named `anythingllm_mcp_servers.json`.

This repo includes a template at [anythingllm_mcp_servers.json](/Volumes/Hub/Code/GitHub/mcp-mariadb-demo/anythingllm_mcp_servers.json).

Copy that file into your AnythingLLM plugins storage directory as:

- macOS desktop: `~/Library/Application Support/anythingllm-desktop/storage/plugins/anythingllm_mcp_servers.json`
- Linux desktop: `~/.config/anythingllm-desktop/storage/plugins/anythingllm_mcp_servers.json`
- Windows desktop: `C:\Users\<usr>\AppData\Roaming\anythingllm-desktop\storage\plugins\anythingllm_mcp_servers.json`
- Docker/self-hosted: `/app/server/storage/plugins/anythingllm_mcp_servers.json`

The template uses absolute paths on this machine so AnythingLLM can launch the server without depending on its own working directory. It also passes `--env-file` explicitly so the repo root `.env` is used even when AnythingLLM starts the process from somewhere else.

## 12. Troubleshooting Checklist

Check these in order:

1. `.env` matches your actual MariaDB host, port, user, password, and database
2. the schema and seed files have been loaded
3. `mariadb -h <host> -P <port> -u <user> -p <database>` works
4. `python src/server.py` starts without import errors
5. the metadata query using `DATABASE()`, `CURRENT_USER()`, `@@hostname`, and `@@port` matches the server you expect
6. if you are using a separate MCP host, VS Code points at the correct remote MCP URL
7. `.vscode/mcp.json` exists and uses `servers`, not `mcpServers`
8. `MCP: List Servers` shows the server you expect
9. VS Code chat has that server's tools enabled
