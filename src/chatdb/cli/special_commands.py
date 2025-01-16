from pathlib import Path
from typing import Dict, Protocol

from rich.markdown import Markdown

from chatdb.agent import AgentRunner
from chatdb.database import TableNotFoundError
from chatdb.deps import CLIAgentDeps


class CommandHandler(Protocol):
    def __call__(self, arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None: ...


def handle_result(arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    database = agent_runner.deps.database
    console = agent_runner.deps.console

    if database.last_query:
        console.print(Markdown(database.last_query.to_markdown()))
    else:
        console.print("No previous query results.")


def handle_clear(arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    agent_runner.clear_message_history()
    agent_runner.deps.console.print("Conversation history cleared.")


def handle_sql(arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    result = agent_runner.deps.database.execute_sql(arg)
    agent_runner.deps.console.print(Markdown(result.to_markdown()))


def handle_schema(arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    database = agent_runner.deps.database
    console = agent_runner.deps.console
    table_names = [name.strip() for name in arg.split(",")] if arg else None
    try:
        schema = database.describe_schema(table_names=table_names)
    except TableNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        return
    console.print(Markdown(f"```\n{schema}\n```"))


def handle_export(arg: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    """Export the most recent query results to a CSV file."""
    console = agent_runner.deps.console

    last_query = agent_runner.deps.database.last_query
    if not last_query or not last_query.rows:
        console.print("[red]No query results to export[/red]")
        return

    # Use provided filename or generate one
    filename = arg if arg else "query_results.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"

    path = Path(filename)
    try:
        with path.open("wt", newline="") as f:
            f.write(last_query.to_csv())
        console.print(f"[green]Results exported to {path.absolute()}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting results: {str(e)}[/red]")


COMMAND_HANDLERS: Dict[str, CommandHandler] = {
    "/result": handle_result,
    "/clear": handle_clear,
    "/sql": handle_sql,
    "/schema": handle_schema,
    "/export": handle_export,
}


def handle_special_command(command: str, agent_runner: AgentRunner[CLIAgentDeps]) -> None:
    command = command.strip()
    if not command.startswith("/"):
        raise ValueError(f"Invalid command format: {command}")

    parts = command.split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    if cmd not in COMMAND_HANDLERS:
        raise ValueError(f"Unknown command: {cmd}")

    COMMAND_HANDLERS[cmd](arg, agent_runner)
