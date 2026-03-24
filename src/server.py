import argparse
import os
from typing import Any, Dict, List, Optional, cast

import pymysql
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("mariadb-demo")


READ_ONLY_PREFIXES = ("select", "show", "describe", "explain")


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_connection() -> pymysql.connections.Connection:
    host = _env("MARIADB_HOST", "127.0.0.1")
    port = int(_env("MARIADB_PORT", "3307"))
    user = _env("MARIADB_USER", "demo_user")
    password = _env("MARIADB_PASSWORD", "demo_password")
    database = _env("MARIADB_DATABASE", "mcp_demo")
    ssl_disabled = _env("MARIADB_SSL_DISABLED", "true").lower() == "true"

    ssl: Optional[Dict[str, Any]] = None
    if not ssl_disabled:
        ssl = {}

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        ssl=ssl,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
    )


def _ensure_read_only(sql: str) -> str:
    statement = sql.strip()
    if not statement:
        raise ValueError("SQL cannot be empty.")
    lowered = statement.lower()
    if not lowered.startswith(READ_ONLY_PREFIXES):
        raise ValueError(
            "Only read-only SQL is allowed in this demo. Use SELECT/SHOW/DESCRIBE/EXPLAIN."
        )
    return statement


@mcp.tool()
def ping_database() -> Dict[str, Any]:
    """Check database connectivity and return server/version info."""
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS database_name, VERSION() AS server_version")
            row = cast(Optional[Dict[str, Any]], cursor.fetchone())
    if row is None:
        raise RuntimeError("Database ping query returned no rows.")
    return {
        "status": "ok",
        "database": row.get("database_name"),
        "server_version": row.get("server_version"),
    }


@mcp.tool()
def list_tables(schema: Optional[str] = None) -> List[str]:
    """List tables in the current database (or a provided schema)."""
    target_schema = schema or _env("MARIADB_DATABASE", "mcp_demo")
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (target_schema,),
            )
            rows = cast(List[Dict[str, Any]], cursor.fetchall())
    return [str(row.get("table_name")) for row in rows if row.get("table_name") is not None]


@mcp.tool()
def run_readonly_query(sql: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Run a read-only SQL query and return up to `limit` rows."""
    statement = _ensure_read_only(sql)
    if limit < 1:
        raise ValueError("limit must be >= 1")

    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(statement)
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

    return rows[: min(limit, 200)]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MariaDB demo MCP server over stdio, streamable HTTP, or SSE."
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "http", "streamable-http", "sse"),
        default="stdio",
        help="Transport to use. Default: stdio. 'http' is accepted as an alias for 'streamable-http'.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for streamable HTTP or SSE transport. Default: 127.0.0.1.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for streamable HTTP or SSE transport. Default: 8000.",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="Endpoint path for streamable HTTP or SSE transport. Default: /mcp.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    transport = "streamable-http" if args.transport == "http" else args.transport

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse", mount_path=args.path)
    else:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.streamable_http_path = args.path
        mcp.run(transport="streamable-http")
