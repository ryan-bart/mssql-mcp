"""
Minimal MSSQL MCP Server for Claude Desktop
Uses pytds (pure Python TDS) - no ODBC driver needed, handles Azure SQL encryption natively.

Setup:
  pip install pytds mcp
  
Config (claude_desktop_config.json):
  "mssql": {
    "command": "python",
    "args": ["C:\\path\\to\\server.py"],
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
import sys
import json
import pytds
from mcp.server.fastmcp import FastMCP

server = FastMCP("mssql-server")


def get_connection():
    """Create a new database connection."""
    return pytds.connect(
        server=os.environ["MSSQL_SERVER"],
        database=os.environ["MSSQL_DATABASE"],
        user=os.environ["MSSQL_USER"],
        password=os.environ["MSSQL_PASSWORD"],
        port=int(os.environ.get("MSSQL_PORT", "1433")),
        as_dict=True,
        autocommit=True,
    )


@server.tool()
def execute_sql(query: str) -> str:
    """Execute a SQL query on the SQL Server and return results as JSON."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if query returns results
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            # Convert rows to list of dicts, handling non-serializable types
            results = []
            for row in rows:
                clean_row = {}
                for col in columns:
                    val = row[col]
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
