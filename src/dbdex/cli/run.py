try:
    import readline
except ImportError:
    import pyreadline3 as readline


from typing import Callable, Sequence

from pydantic_ai.models import KnownModelName
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt

from dbdex.agent import get_agent_runner
from dbdex.cli.special_commands import COMMAND_HANDLERS, handle_special_command
from dbdex.database import Database
from dbdex.deps import CLIAgentDeps
from dbdex.llm import build_model_from_name_and_api_key

EXIT_COMMANDS = ["/quit", "/exit", "/q"]


def get_completer(autocompletes: Sequence[str]) -> Callable[[str, int], str | None]:
    def completer(text: str, state: int) -> str | None:
        # List of commands to complete from
        matches = [cmd for cmd in autocompletes if cmd.lower().startswith(text.lower())]
        return matches[state] if state < len(matches) else None

    return completer


async def run(
    db_uri: str,
    model_name: KnownModelName,
    api_key: str | None = None,
    max_return_values: int = 200,
    stream: bool = False,
) -> None:
    """Run the DBdex CLI.

    Args:
        model_name: Name of the LLM model to use
        api_key: API key for the model service
        db_uri: Database connection URI. Defaults to sqlite:///db.sqlite3
        max_return_values: Maximum number of values to return to the LLM from a DB query
        stream: Whether to stream responses from the LLM
    """
    console = Console()
    database = Database(db_uri)
    deps = CLIAgentDeps(database=database, console=console, max_return_values=max_return_values)
    model = build_model_from_name_and_api_key(model_name, api_key)
    agent_runner = get_agent_runner(model, deps)

    autocompletes = list(COMMAND_HANDLERS) + EXIT_COMMANDS + database.table_names

    readline.set_completer(get_completer(autocompletes))
    readline.parse_and_bind("tab: complete")  # Use Tab for auto-completion
    readline.set_completer_delims(" \t\n;")

    console.print(
        "Welcome to DBdex CLI! Type '/exit' or '/q' to exit. What would you like to know about your database? "
    )
    while True:
        query = Prompt.ask("You").strip()
        if not query:
            continue

        if query.lower() in EXIT_COMMANDS:
            break

        if query.startswith("/"):
            handle_special_command(query, agent_runner)
            continue

        with Live(console=console, vertical_overflow="visible") as live_console:
            live_console.update("DBdex:  ...")

            if stream:
                async for streamed_message in agent_runner.run_stream(query):
                    live_console.update(Markdown("DBdex: " + streamed_message))
            else:
                response = await agent_runner.run(query)
                live_console.update(Markdown("DBdex: " + response.data))
