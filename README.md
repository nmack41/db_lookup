# ChatDB

Use AI to query your database using natural language. ChatDB provides a CLI and web interface for interacting with databases using various AI models including OpenAI GPT-4, Anthropic Claude, and Mistral.

## Features

- Natural language to SQL translation
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

Clone the repository and install the package:

```
git clone https://github.com/yourusername/chatdb.git
cd chatdb
make install
```

## Usage

### CLI Interface

Run the CLI with your model choice and API key:

```
# Using OpenAI
python -m chatdb.cli --model-name openai:gpt-4 --api-key your_api_key --db-uri postgresql://user:pass@localhost:5432/dbname

```

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

```
# Install development dependencies
make install

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

