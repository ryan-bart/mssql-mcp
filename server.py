"""
Minimal MSSQL MCP Server for Claude Desktop
Uses pyodbc with ODBC Driver 17 for SQL Server - handles Azure SQL encryption natively.

Setup:
  pip install pyodbc mcp

Config (claude_desktop_config.json):
  "mssql": {
    "command": "C:\\Users\\ryan.bartusek\\AppData\\Local\\anaconda3\\python.exe",
    "args": ["C:\\github\\mssql-mcp\\server.py"],
    "env": {
      "MSSQL_SERVER": "your-server.database.windows.net",
      "MSSQL_DATABASE": "your_database",
      "MSSQL_USER": "your_user",
      "MSSQL_PASSWORD": "your_password",
      "MSSQL_PORT": "1433",
      "MSSQL_READONLY": "true"
    }
  }
"""

import os
import json
import re
import pyodbc
from mcp.server.fastmcp import FastMCP

server = FastMCP("mssql-server")

READONLY = os.environ.get("MSSQL_READONLY", "true").lower() == "true"

WRITE_KEYWORDS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE|MERGE|GRANT|REVOKE)\b",
    re.IGNORECASE
)


def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.environ['MSSQL_SERVER']},{os.environ.get('MSSQL_PORT', '1433')};"
        f"DATABASE={os.environ['MSSQL_DATABASE']};"
        f"UID={os.environ['MSSQL_USER']};"
        f"PWD={os.environ['MSSQL_PASSWORD']};"
        f"Encrypt=yes;TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str, autocommit=True)


def fetch_results(cursor) -> str:
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    results = []
    for row in rows:
        clean_row = {}
        for i, col in enumerate(columns):
            val = row[i]
            if val is None:
                clean_row[col] = None
            elif isinstance(val, (int, float, bool)):
                clean_row[col] = val
            else:
                clean_row[col] = str(val)
        results.append(clean_row)
    return json.dumps(results, indent=2)


@server.tool()
def execute_sql(query: str) -> str:
    """Execute a SQL query and return results as JSON. In read-only mode, only SELECT statements are permitted."""
    if READONLY and WRITE_KEYWORDS.match(query.strip()):
        return "Error: Server is in read-only mode. Only SELECT queries are allowed."
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.description:
            result = fetch_results(cursor)
        else:
            result = f"Query executed successfully. Rows affected: {cursor.rowcount}"
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"


@server.tool()
def list_tables(schema: str = None) -> str:
    """List all tables and views in the database. Optionally filter by schema name (e.g. 'dw', 'Stg_EpicUS')."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if schema:
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = ?
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """, schema)
        else:
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
        result = fetch_results(cursor)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@server.tool()
def describe_table(table_name: str, schema: str = "dbo") -> str:
    """
    Describe the columns of a table or view.
    Returns column name, data type, max length, and nullability.
    Example: describe_table('FactPolicyLine', 'dw')
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
              AND TABLE_SCHEMA = ?
            ORDER BY ORDINAL_POSITION
        """, table_name, schema)
        if not cursor.description:
            return f"No columns found for {schema}.{table_name}. Check the table name and schema."
        result = fetch_results(cursor)
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return f"Error describing table: {str(e)}"


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()