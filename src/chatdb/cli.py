import argparse
import readline
from collections import defaultdict

import logfire
from pydantic_ai.models import KnownModelName
from rich.console import Console
from rich.markdown import Markdown

from chatdb.agent import get_agent_runner
from chatdb.database import Database
from chatdb.deps import AgentDeps

logfire.configure()


def completer(text: str, state: int) -> str | None:
    # List of commands to complete from
    commands = ["/clear", "/results", "/quit"]
    matches = [cmd for cmd in commands if cmd.startswith(text)]
    return matches[state] if state < len(matches) else None


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")  # Use Tab for auto-completion


def main(model_name: KnownModelName, api_key: str, db_uri: str) -> None:
    """Run the ChatDB CLI.

    Args:
        model_name: Name of the LLM model to use
        api_key: API key for the model service
        db_uri: Database connection URI. Defaults to sqlite:///db.sqlite3
    """
    console = Console()
    database = Database(db_uri)
    deps = AgentDeps(database=database, console=console)
    agent_runner = get_agent_runner(model_name, api_key, deps=deps)

    console.print("Welcome to ChatDB CLI. Type 'exit' to exit. Enter a question: ")
    while True:
        query = input(">").strip()
        if not query:
            continue

        if query.lower() in ["/quit", "exit", "quit", "q"]:
            break

        if query == "/results":
            # Display previous query results
            if database.last_query:
                console.print(Markdown(database.last_query.to_markdown()))
            else:
                console.print("No previous query results.")
            continue

        if query == "/clear":
            agent_runner.clear_message_history()
            console.print("Conversation history cleared.")
            continue

        response = agent_runner.run_sync(query)
        console.print(Markdown(response))


def format_model_options(model_options: list[str]) -> str:
    # Group models by provider
    grouped = defaultdict(list)
    for item in model_options:
        if item == "test":
            continue
        provider, model = item.split(":")
        grouped[provider].append(model)

    # Format the output
    formatted_lines = [f"- {provider}: {', '.join(models)}" for provider, models in grouped.items()]
    return "\n".join(formatted_lines)


if __name__ == "__main__":
    MODEL_OPTIONS = [
        model_name
        for model_name in KnownModelName.__args__
        if model_name != "test" and not model_name.startswith("google-vertex")
    ]

    parser = argparse.ArgumentParser(description="ChatDB CLI", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--db-uri",
        type=str,
        help="Database connection URI",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="Name of the LLM model to use, in format provider:model (e.g. openai:gpt-4o). "
        "Choices (not exhaustive, more may be supported):\n" + format_model_options(MODEL_OPTIONS),
        metavar="PROVIDER:MODEL",
        # Don't strictly enforce choices since new models may be added
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="API key for the model service",
    )

    args = parser.parse_args()
    main(
        model_name=args.model_name,
        api_key=args.api_key,
        db_uri=args.db_uri,
    )
