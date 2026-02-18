# mssql-mcp

A minimal MCP (Model Context Protocol) server that connects Claude Desktop to Microsoft SQL Server, including Azure SQL Database.

## Requirements

- Python (Anaconda recommended)
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Claude Desktop

## Installation

```bash
pip install pyodbc mcp
```

## Setup

1. Clone the repo and note the path to `server.py`
2. Add the following to your `claude_desktop_config.json` (found at `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mssql": {
      "command": "C:\\path\\to\\your\\python.exe",
      "args": ["C:\\path\\to\\mssql-mcp\\server.py"],
      "env": {
        "MSSQL_SERVER": "your-server.database.windows.net",
        "MSSQL_DATABASE": "your_database",
        "MSSQL_USER": "your_user",
        "MSSQL_PASSWORD": "your_password",
        "MSSQL_PORT": "1433",
        "MSSQL_READONLY": "true"
      }
    }
  }
}
```

3. Restart Claude Desktop
4. Click the hammer 🔨 icon in the chat input — the available tools should appear

## Tools

**`execute_sql`** — Run a SQL query and return results as JSON. In read-only mode, only SELECT statements are allowed.

**`list_tables`** — List all tables and views in the database. Optionally filter by schema name (e.g. `dw`, `Stg_EpicUS`).

**`describe_table`** — Return column names, data types, and nullability for a given table. Accepts `table_name` and `schema` parameters.

## Read-Only Mode

Set `MSSQL_READONLY=true` in your env config to block any write operations (INSERT, UPDATE, DELETE, DROP, etc.). This is enabled by default. Set to `false` to allow write queries.

## Usage

Once connected, you can ask Claude natural language questions about your data and it will translate them into SQL queries and return results directly in the chat. Use `list_tables` and `describe_table` to help Claude understand your schema without having to explain it manually.

## Notes

- Azure SQL requires encryption — this is handled automatically via the ODBC connection string
- Use `where python` in your terminal to find the correct Python executable path
- The server runs over stdio and will appear as a blinking cursor if launched manually — this is normal
