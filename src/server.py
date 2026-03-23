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
    database = _env("MARIADB_DATABASE", "demo_mcp")
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
    target_schema = schema or _env("MARIADB_DATABASE", "demo_mcp")
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


if __name__ == "__main__":
    mcp.run()
