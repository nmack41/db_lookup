import readline
from typing import Callable, Sequence

from pydantic_ai.models import KnownModelName
from rich.console import Console
from rich.markdown import Markdown

from chatdb.agent import get_agent_runner
from chatdb.cli.special_commands import COMMAND_HANDLERS, handle_special_command
from chatdb.database import Database
from chatdb.deps import CLIAgentDeps


def get_completer(autocompletes: Sequence[str]) -> Callable[[str, int], str | None]:
    def completer(text: str, state: int) -> str | None:
        # List of commands to complete from
        matches = [cmd for cmd in autocompletes if cmd.lower().startswith(text.lower())]
        return matches[state] if state < len(matches) else None

    return completer


def run(model_name: KnownModelName, api_key: str, db_uri: str, max_return_values: int = 200) -> None:
    """Run the ChatDB CLI.

    Args:
        model_name: Name of the LLM model to use
        api_key: API key for the model service
        db_uri: Database connection URI. Defaults to sqlite:///db.sqlite3
        max_return_values: Maximum number of values to return to the LLM from a DB query
    """
    console = Console()
    database = Database(db_uri)
    deps = CLIAgentDeps(database=database, console=console, max_return_values=max_return_values)
    agent_runner = get_agent_runner(model_name, api_key, deps=deps)

    autocompletes = list(COMMAND_HANDLERS) + database.table_names

    readline.set_completer(get_completer(autocompletes))
    readline.parse_and_bind("tab: complete")  # Use Tab for auto-completion
    readline.set_completer_delims(" \t\n;")

    console.print("Welcome to ChatDB CLI. Type 'exit' to exit. Enter a question: ")
    while True:
        query = input(">").strip()
        if not query:
            continue

        if query.lower() in ["/quit", "exit", "quit", "q"]:
            break

        if query.startswith("/"):
            handle_special_command(query, agent_runner)
            continue

        response = agent_runner.run_sync(query)
        console.print(Markdown(response.data))
