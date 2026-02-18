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
      "MSSQL_PORT": "1433"
    }
  }
"""

import os
import json
import pyodbc
from mcp.server.fastmcp import FastMCP

server = FastMCP("mssql-server")


def get_connection():
    """Create a new database connection."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.environ['MSSQL_SERVER']},{os.environ.get('MSSQL_PORT', '1433')};"
        f"DATABASE={os.environ['MSSQL_DATABASE']};"
        f"UID={os.environ['MSSQL_USER']};"
        f"PWD={os.environ['MSSQL_PASSWORD']};"
        f"Encrypt=yes;TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str, autocommit=True)


@server.tool()
def execute_sql(query: str) -> str:
    """Execute a SQL query on the SQL Server and return results as JSON."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
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
            cursor.close()
            conn.close()
            return json.dumps(results, indent=2)
        else:
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            return f"Query executed successfully. Rows affected: {affected}"

    except Exception as e:
        return f"Error executing query: {str(e)}"


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()