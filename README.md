Based on dbdex: https://github.com/Finndersen/dbdex to include only local ollama models

# DBdex

Like a Pokédex, but for your database. Uses AI to answer questions about your database data or schema using natural language.

## Features

- Automatically generates and executes SQL queries based on natural language input, and displays results
- Support all major databases (PostgreSQL, MySQL, Oracle, MSSQL, SQLite)
- Support for multiple AI providers (OpenAI, Anthropic, Mistral, Google, Groq, Ollama)
- Automatic schema introspection
- Interactive CLI interface with Markdown-formatted responses and tab completion of commands and table names
- Query history and result tracking
- Efficient handling & display of large result sets (avoids having the LLM generate the data in its response)

TODO:

- Streaming responses
- Web interface with graph plotting

## Example

```md
Welcome to DBdex CLI! Type '/exit' or '/q' to exit. What would you like to know about your database?
You: Provide a brief description of each table
DBdex: Okay, here's a brief description of each table:

• Categories: Stores information about product categories, such as the category name and description.  
 • Customers: Contains information about customers, such as their company name, contact details, and address.
• Employees: Stores information about employees, such as their name, job title, and contact information.  
 • Order Details: Contains details about individual items within an order, such as the product, quantity, and price.  
 • Orders: Contains information about customer orders, including order date, ship details, and associated customer and employee IDs.  
 • Products: Stores information about products, such as the product name, category, supplier, and price.

You: How many customers are there?
DBdex: There are 93 customers.
You: Show the name, phone number and city for all customers from Germany

CompanyName Phone City  
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alfreds Futterkiste 030-0074321 Berlin  
 Blauer See Delikatessen 0621-08460 Mannheim  
 Drachenblut Delikatessen 0241-039123 Aachen  
 Frankenversand 089-0877310 München  
 Königlich Essen 0555-09876 Brandenburg  
 Lehmanns Marktstand 069-0245984 Frankfurt a.M.

DBdex: Okay, I've displayed the results showing the company name, phone number, and city for all customers from Germany.
You: /export customers_germany.csv
Results exported to customers_germany.csv
```

## Installation

Install directly from GitHub, specifying the database drivers you need:

```
# Install with all database drivers
pip install git+https://github.com/Finndersen/dbdex.git[all]

# Install with specific database drivers (choose one or more)
pip install git+https://github.com/Finndersen/dbdex.git[postgres, mysql, oracle, mssql]
```

## Usage

### CLI Interface

Run the CLI with your model choice and API key:

```
# Using OpenAI
python -m dbdex \
    --model provider:model_name \
    --api-key your_api_key \
    --db-uri postgresql://user:pass@localhost:5432/dbname
```

The LLM API key can be provided as CLI argument or as environment variable (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc.).

Supported databases and their connection strings:

- PostgreSQL: `postgresql://user:pass@localhost:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/dbname`
- Oracle: `oracle+cx_oracle://user:pass@localhost:1521/dbname`
- MSSQL: `mssql+pyodbc://user:pass@localhost/dbname`
- SQLite: `sqlite:///path/to/db.sqlite3`

Use `--help` to see available model options (newer ones not in the list should also work)

CLI commands:

- `/quit`, `/q` or `/exit` - Exit the CLI
- `/clear` - Clear conversation history (context provided to the LLM)
- `/sql <query>` - Execute SQL query directly
- `/schema [table1,table2,...]` - Show database schema (optionally for specific tables)
- `/result` - Show details & results of the last executed query by the LLM
- `/export [filename]` - Export last query results to CSV (defaults to query_results.csv)

## Logging

DBdex uses [Logfire](https://github.com/logfire-sh/logfire) for logging (via `pydantic-ai`).
Check [here](https://logfire.pydantic.dev/docs/#logfire) for how to authorize and configure your Logfire project to receive logs from DBdex.

Use the `--debug` CLI option to show logs in the console.

## Development

Clone the repository and install in development mode:

```
git clone https://github.com/yourusername/dbdex.git
cd dbdex
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
