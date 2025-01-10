# ChatDB

Use AI to query your database using natural language. ChatDB provides a CLI and web interface for interacting with databases using various AI models including OpenAI GPT-4, Anthropic Claude, and Mistral.

## Features

- Natural language to SQL translation
- Support all major databases (PostgreSQL, MySQL, Oracle, MSSQL, SQLite)
- Support for multiple AI providers:
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
  - Mistral
  - Google (Gemini, VertexAI)
  - Groq
  - Ollama
- Automatic schema detection
- SQL query execution with formatted results
- Markdown-formatted responses
- Interactive CLI interface

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
python -m chatdb.cli --model-name provider:model_name --api-key your_api_key --db-uri postgresql://user:pass@localhost:5432/dbname

```

Supported databases and their connection strings:
- PostgreSQL: `postgresql://user:pass@localhost:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/dbname`
- Oracle: `oracle+cx_oracle://user:pass@localhost:1521/dbname`
- MSSQL: `mssql+pyodbc://user:pass@localhost/dbname`
- SQLite: `sqlite:///path/to/db.sqlite3`

Use `--help` to see all available model options. 

CLI commands:
- Type 'exit', 'quit', 'q', 'e', 'bye' to exit
- Type '/clear' to clear message history


## Example

```python
from chatdb.agent import get_agent
from chatdb.database import Database
from chatdb.models import KnownModelName

# Connect to database
db = Database("postgresql://user:pass@localhost:5432/dbname")

# Initialize agent
agent = get_agent(
    model_name=KnownModelName("openai:gpt-4"),
    api_key="your-api-key",
    database=db
)

# Query in natural language
response = agent.chat("Show me the top 10 customers by order value")
print(response)
```

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

## Configuration

The project uses `pyproject.toml` for configuration:
- Python version: >=3.10
- Code style: 120 character line length
- Strict type checking with mypy
- Comprehensive linting with ruff

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
- [pydantic-ai](https://github.com/jxnl/pydantic-ai) - AI model integration
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database connectivity

