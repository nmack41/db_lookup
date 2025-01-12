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


COMMAND_HANDLERS: Dict[str, CommandHandler] = {
    "/result": handle_result,
    "/clear": handle_clear,
    "/sql": handle_sql,
    "/schema": handle_schema,
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
