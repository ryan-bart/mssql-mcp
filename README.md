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
        "MSSQL_PORT": "1433"
      }
    }
  }
}
```

3. Restart Claude Desktop
4. Click the hammer 🔨 icon in the chat input — `execute_sql` should appear as an available tool

## Usage

Once connected, you can ask Claude natural language questions about your data and it will translate them into SQL queries and return results directly in the chat.

## Notes

- Azure SQL requires encryption — this is handled automatically via the ODBC connection string
- Use `where python` in your terminal to find the correct Python executable path
- The server runs over stdio and will appear as a blinking cursor if launched manually — this is normal
