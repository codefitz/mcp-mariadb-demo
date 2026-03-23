What we’re building

You’ll end up with:
1.	MariaDB running locally on macOS
2.	A demo database with realistic IT/helpdesk-style data
3.	The MariaDB MCP server running locally
4.	An MCP client such as Cursor or Claude Desktop connected to it
5.	Optional vector search enabled with OpenAI embeddings later on  ￼

⸻

Part 1. Install MariaDB locally on macOS

MariaDB’s current macOS docs say to install via Homebrew:

```shell
brew install mariadb
brew services start mariadb
```
Then connect with:

```shell
mariadb
```

or:

```shell
sudo mysql -u root
```

On Apple Silicon Macs, the main MariaDB config file is typically:

```shell
/opt/homebrew/etc/my.cnf
```

Those are the official current macOS instructions.

1. Check whether Homebrew is installed

```shell
brew --version
```

If not, install it:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

That installer is the one MariaDB’s macOS docs point to.  ￼

2. Install and start MariaDB

```shell
brew install mariadb
brew services start mariadb
```

3. Confirm it is running

```shell
brew services list | grep mariadb
mariadb --version
```

4. Open the MariaDB shell

```shell
mariadb
```

If that works, the database engine is alive and purring.

⸻

Part 2. Create a proper local database user

For MCP, use a dedicated user, not your main admin account. The MariaDB MCP repo explicitly recommends a dedicated minimal-privilege DB user, and also notes that MCP_READ_ONLY=true is helpful but not a substitute for proper database permissions.  ￼

Inside the MariaDB shell:

```SQL
CREATE DATABASE mcp_demo;
CREATE USER 'mcp_user'@'localhost' IDENTIFIED BY 'StrongLocalPassword123!';
GRANT ALL PRIVILEGES ON mcp_demo.* TO 'mcp_user'@'localhost';
FLUSH PRIVILEGES;
```

For the first tutorial pass, ALL PRIVILEGES on just the demo DB is fine. Later, for safer testing, you can reduce that to read-only.

⸻

Part 3. Create demo data

For a demo, I would not use a toy “employees” database. It looks nice for five minutes and teaches very little.

A better fit for MCP is a small IT operations/helpdesk dataset:
- users
- assets
- tickets
- knowledge articles

That gives you both:
- structured SQL queries
- unstructured text you can later push into vector search

3.1 Create the schema

Save this as `db/init/demo_schema.sql`:

```SQL
USE mcp_demo;

DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS knowledge_articles;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_tag VARCHAR(50) NOT NULL UNIQUE,
    asset_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    assigned_user_id INT NULL,
    purchase_date DATE,
    warranty_expiry DATE,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (assigned_user_id) REFERENCES users(user_id)
);

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    opened_by_user_id INT NOT NULL,
    assigned_team VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (opened_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE knowledge_articles (
    article_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    body TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL
);
```

3.2 Seed the tables

Save this as `db/init/demo_data.sql`:

```SQL
USE mcp_demo;

INSERT INTO users (full_name, department, email, location) VALUES
('Alice Carter', 'Finance', 'alice.carter@example.local', 'London'),
('Ben Morris', 'IT', 'ben.morris@example.local', 'Manchester'),
('Chloe Singh', 'HR', 'chloe.singh@example.local', 'Birmingham'),
('Daniel Reed', 'Sales', 'daniel.reed@example.local', 'London'),
('Emma Hughes', 'Operations', 'emma.hughes@example.local', 'Leeds');

INSERT INTO assets (asset_tag, asset_type, manufacturer, model, serial_number, assigned_user_id, purchase_date, warranty_expiry, status) VALUES
('LAP-1001', 'Laptop', 'Dell', 'Latitude 7440', 'SN-DEL-7440-001', 1, '2024-02-10', '2027-02-10', 'In Use'),
('LAP-1002', 'Laptop', 'Lenovo', 'ThinkPad T14', 'SN-LEN-T14-002', 2, '2023-11-05', '2026-11-05', 'In Use'),
('PHN-2001', 'Phone', 'Apple', 'iPhone 15', 'SN-APL-IP15-003', 4, '2024-06-15', '2026-06-15', 'In Use'),
('MON-3001', 'Monitor', 'LG', 'UltraFine 27', 'SN-LG-UF27-004', 1, '2022-09-01', '2025-09-01', 'In Repair'),
('LAP-1003', 'Laptop', 'HP', 'EliteBook 840', 'SN-HP-840-005', NULL, '2025-01-08', '2028-01-08', 'In Stock');

INSERT INTO tickets (title, description, priority, status, category, opened_by_user_id, assigned_team, created_at, updated_at) VALUES
('Laptop will not connect to VPN', 'User reports repeated VPN failures on home broadband. Error appears after MFA approval.', 'High', 'Open', 'Network', 1, 'Service Desk', '2026-03-18 09:15:00', '2026-03-18 10:00:00'),
('Monitor flickering intermittently', 'External display flickers after waking from sleep. Suspected cable or dock issue.', 'Medium', 'In Progress', 'Hardware', 1, 'End User Computing', '2026-03-17 14:20:00', '2026-03-18 08:30:00'),
('Password reset not syncing to email', 'User changed AD password but mobile mail app still rejects credentials.', 'High', 'Resolved', 'Identity', 3, 'Identity Team', '2026-03-15 11:00:00', '2026-03-15 15:45:00'),
('New starter laptop request', 'Prepare and assign a standard laptop build for new joiner starting next Monday.', 'Low', 'Open', 'Provisioning', 5, 'Asset Team', '2026-03-19 13:10:00', '2026-03-19 13:10:00'),
('Slow performance on finance laptop', 'Laptop becomes slow when opening spreadsheets and Teams calls together.', 'Medium', 'Open', 'Performance', 1, 'End User Computing', '2026-03-20 10:25:00', '2026-03-20 10:25:00');

INSERT INTO knowledge_articles (title, category, body, author, created_at) VALUES
('How to troubleshoot VPN failures', 'Network',
'Check whether the user can reach the internet, confirm the VPN client version, verify MFA success, and review whether split tunnelling policies changed. If the issue started after a password change, test cached credentials and re-authentication.',
'Ben Morris', '2026-03-01 09:00:00'),

('Resolving monitor flicker on USB-C docks', 'Hardware',
'Monitor flicker is commonly caused by cable quality, dock firmware, refresh rate mismatch, or power-saving behaviour. Test with a direct cable, update dock firmware, and confirm display settings after wake from sleep.',
'Ben Morris', '2026-02-25 10:30:00'),

('Mobile mail still prompting after password reset', 'Identity',
'If a password has been reset, mobile mail clients may continue using cached credentials. Remove and re-add the account or update saved credentials in the mail application. In some cases conditional access delays can cause short-lived sign-in failures.',
'Chloe Singh', '2026-02-28 16:00:00'),

('Standard new starter laptop process', 'Provisioning',
'Assign an available device from stock, apply the standard image, confirm encryption, install endpoint protection, enrol into device management, and record the asset assignment against the user before handover.',
'Emma Hughes', '2026-03-05 08:45:00');
```

3.3 Import both files

```shell
mariadb -u mcp_user -p < demo_schema.sql
mariadb -u mcp_user -p < demo_data.sql
```

Or from inside the MariaDB shell:

```shell
SOURCE /full/path/to/demo_schema.sql;
SOURCE /full/path/to/demo_data.sql;
```

3.4 Test the data

```shell
mariadb -u mcp_user -p mcp_demo
```
Then:

```SQL
SHOW TABLES;
SELECT * FROM users;
SELECT ticket_id, title, status, assigned_team FROM tickets;
SELECT title, category FROM knowledge_articles;
```

At this point, you have a decent little sandbox instead of a cardboard database with a fake moustache.

⸻

Part 4. Install the MariaDB MCP server

The official MariaDB MCP repo says the requirements are:
- Python 3.11
- uv
- MariaDB server
- then: clone repo, uv lock, uv sync, create .env, run server.py  ￼

4.1 Install Python 3.11

Check what you already have:

```shell
python3 --version
```

If needed:

```shell
brew install python@3.11
```

4.2 Install uv

The repo’s setup section shows:

```shell
pip install uv
```

So:

```shell
python3.11 -m pip install uv
```

That matches the project instructions.  ￼

4.3 Clone the MariaDB MCP repo

```shell
git clone https://github.com/MariaDB/mcp.git mariadb-mcp
cd mariadb-mcp
```

4.4 Install dependencies

The repo setup uses:

```shell
uv lock
uv sync
```

So run:

```shell
uv lock
uv sync
```

⸻

Part 5. Configure the MCP server

The repo documents these main environment variables:
- DB_HOST
- DB_PORT
- DB_USER
- DB_PASSWORD
- DB_NAME
- MCP_READ_ONLY
- optional embedding settings such as EMBEDDING_PROVIDER and OPENAI_API_KEY for vector workflows  ￼

5.1 Create the .env file

Inside the mariadb-mcp folder, create .env:

```shell
vi .env
```

Paste this:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=mcp_user
DB_PASSWORD=StrongLocalPassword123!
DB_NAME=mcp_demo
MCP_READ_ONLY=true
```

That is enough for the SQL side.

Optional vector settings later

When you want semantic search as well, expand the same file:

```ini
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

The official repo lists OpenAI, Gemini, and HuggingFace as supported embedding providers.  ￼

⸻

Part 6. Run the MCP server

The repo documents three transports:
- `uv run server.py` for stdio
- `uv run server.py --transport sse --host 127.0.0.1 --port 9001`
- `uv run server.py --transport http --host 127.0.0.1 --port 9001 --path /mcp`

For local desktop clients, start with stdio because it is the simplest.

6.1 Start it

```shell
uv run src/server.py
```

If that runs without errors, the MCP server is up.  ￼

⸻

Part 7. Connect an MCP client

[How To](HOWTOMCP.md)

The repo includes sample client configs for stdio, SSE, and HTTP. For a local Mac setup, again, use stdio first.  ￼

7.1 Example MCP config for a desktop client

Use the repo’s stdio pattern and adapt the paths:

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

That is the official pattern shown in the repo for direct-command stdio integration.  ￼

If your client prefers HTTP instead, start the server with:

```shell
uv run src/server.py --transport http --host 127.0.0.1 --port 9001 --path /mcp
```

Then use:

```json
{
  "servers": {
    "mariadb-mcp-server": {
      "url": "http://127.0.0.1:9001/mcp",
      "type": "streamable-http"
    }
  }
}
```

That also matches the repo examples.  ￼

⸻

Part 8. What the MCP server can do

The MariaDB MCP server exposes tools for:
- listing databases
- listing tables
- getting schema
- executing read-only SQL
- creating databases
- and, when embeddings are configured, managing vector stores and semantic search  ￼

So once connected, your MCP client should be able to do things like:
- “List the tables in mcp_demo”
- “Show me tickets opened by Alice Carter”
- “Which assets are in repair?”
- “Summarise open network issues”

⸻

Part 9. First SQL prompts to test in the client

Use these first:

Query 1

`“List all tables in the demo database.”`

Query 2

`“Show the schema for the tickets table.”`

Query 3

`“Find all open tickets with High priority.”`

Expected SQL shape:

```sql
SELECT ticket_id, title, priority, status
FROM tickets
WHERE status = 'Open' AND priority = 'High';
```

Query 4

`“Which user has the most tickets?”`

Expected SQL shape:

```sql
SELECT u.full_name, COUNT(*) AS ticket_count
FROM tickets t
JOIN users u ON t.opened_by_user_id = u.user_id
GROUP BY u.full_name
ORDER BY ticket_count DESC;
```

Query 5

`“Show assets assigned to Alice Carter.”`

Expected SQL shape:

```sql
SELECT a.asset_tag, a.asset_type, a.manufacturer, a.model, a.status
FROM assets a
JOIN users u ON a.assigned_user_id = u.user_id
WHERE u.full_name = 'Alice Carter';
```

⸻

Part 10. Add vector search later

The real sparkle comes when you enable embeddings. The MariaDB blog says the MCP server combines standard SQL operations with vector-based semantic search, and the repo documents vector store tools plus support for OpenAI, Gemini, and HuggingFace embedding providers. MariaDB Community Server 11.7 added vector search with a VECTOR() type and vector functions.  ￼

10.1 Why your knowledge_articles table matters

Your normal relational tables are great for:
- counts
- joins
- filters
- reports

But knowledge_articles.body is better for:
- “find articles about cached credentials”
- “what doc sounds most relevant to VPN MFA failures?”
- “which article matches monitor flicker after wake?”

That is exactly where vector search earns its keep.

10.2 Enable embeddings

Update `.env`:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=mcp_user
DB_PASSWORD=StrongLocalPassword123!
DB_NAME=mcp_demo
MCP_READ_ONLY=true
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

10.3 What the vector store expects

The repo describes a vector store table shape using:
- id
- document
- embedding
- metadata  ￼

And it documents example vector tool calls for:
- creating a vector store
- inserting documents
- semantic search  ￼

So your next phase is:
1.	Create a vector store in mcp_demo
2.	Insert the text from knowledge_articles
3.	Search it semantically from the client

⸻

Part 11. Recommended learning path

Do it in this order:

Phase A

Get MariaDB working locally.

Phase B

Load the demo schema and data.

Phase C

Get MCP working in read-only SQL mode.

Phase D

Test natural-language database queries.

Phase E

Add embeddings and vector search.

That order matters. If you try to do SQL, MCP, desktop config, vectors, API keys, and semantic search all in one leap, the whole thing turns into spaghetti wearing a trench coat.

⸻

Part 12. Common local Mac issues

MariaDB won’t connect

Check:

```shell
brew services list | grep mariadb
```

Then try:

```shell
mariadb
```

The official docs also note Homebrew-managed startup on macOS.  ￼

MCP server starts but client cannot use it

Usually one of these:
- wrong path to the repo
- wrong path to .env
- wrong Python/uv
- bad DB credentials
- desktop client config JSON is malformed

Vector features do not work

Usually one of these:
- MariaDB version is too old
- embedding provider not configured
- API key missing
- trying vector tools before setting EMBEDDING_PROVIDER  ￼
