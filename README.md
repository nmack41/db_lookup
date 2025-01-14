# ChatDB

Use AI to query your database using natural language. Ask questions about your schema, data or optimisation suggestions.

## Features

- Automatically generates and executes SQL queries based on natural language input
- Support all major databases (PostgreSQL, MySQL, Oracle, MSSQL, SQLite)
- Support for multiple AI providers (OpenAI, Anthropic, Mistral, Google, Groq, Ollama)
- Automatic schema introspection
- Interactive CLI interface with Markdown-formatted responses and tab completion
- Query history and result tracking
- Efficient handling & display of large result sets (avoids having the LLM generate the data in its response)

TODO:
- Streaming responses
- Web interface with graph plotting


## Installation

Install directly from GitHub, specifying the database drivers you need:

```
# Install with all database drivers
pip install git+https://github.com/Finndersen/chatdb.git[all]

# Install with specific database drivers (choose one or more)
pip install git+https://github.com/Finndersen/chatdb.git[postgres, mysql, oracle, mssql]
```


## Usage

### CLI Interface

Run the CLI with your model choice and API key:

```
# Using OpenAI
python -m chatdb \
    --model provider:model_name \
    --api-key your_api_key \
    --db-uri postgresql://user:pass@localhost:5432/dbname

```

Supported databases and their connection strings:
- PostgreSQL: `postgresql://user:pass@localhost:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/dbname`
- Oracle: `oracle+cx_oracle://user:pass@localhost:1521/dbname`
- MSSQL: `mssql+pyodbc://user:pass@localhost/dbname`
- SQLite: `sqlite:///path/to/db.sqlite3`

Use `--help` to see available model options (newer ones not in the list should also work)

CLI commands:
- `/quit` or `/exit` - Exit the CLI
- `/clear` - Clear conversation history (context provided to the LLM)
- `/sql <query>` - Execute SQL query directly
- `/schema [table1,table2,...]` - Show database schema (optionally for specific tables)
- `/result` - Show details & results of the last executed query


## Logging

ChatDB uses [Logfire](https://github.com/logfire-sh/logfire) for logging (via `pydantic-ai`). 
Check [here](https://logfire.pydantic.dev/docs/#logfire) for how to authorize and configure your Logfire project to receive logs from ChatDB.

Use the `--log-level` option to control logging verbosity:
- `DEBUG` - Show all debug information
- `INFO` - Show general information (default)
- `WARNING` - Show only warnings and errors
- `ERROR` - Show only errors
- `CRITICAL` - Show only critical errors


## Development

Clone the repository and install in development mode:

```
git clone https://github.com/yourusername/chatdb.git
cd chatdb
make install
```

Development commands:

```
# Run tests
make test

# Format code
make format

# Run linters and type checking
make lint
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License

## Credits

Built with:
- [pydantic-ai](https://github.com/jxnl/pydantic-ai) - AI model integration with [Logfire](https://github.com/logfire-sh/logfire) logging
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database connectivity & schema introspection
- [Rich](https://github.com/Textualize/rich) - Rich text rendering
- [Readline](https://docs.python.org/3/library/readline.html) - Tab completion




