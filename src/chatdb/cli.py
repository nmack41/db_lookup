import argparse
from collections import defaultdict

import logfire
from pydantic_ai.models import KnownModelName
from rich.console import Console
from rich.markdown import Markdown

from chatdb.agent import AgentDeps, get_agent
from chatdb.database import Database

logfire.configure()


def main(model_name: KnownModelName, api_key: str, db_uri: str) -> None:
    """Run the ChatDB CLI.

    Args:
        model_name: Name of the LLM model to use
        api_key: API key for the model service
        db_uri: Database connection URI. Defaults to sqlite:///db.sqlite3
    """
    console = Console()
    console.print("Welcome to ChatDB CLI. Type 'exit' to exit. Enter a question: ")
    database = Database(db_uri)
    agent = get_agent(model_name, api_key, database)
    message_history = None
    while True:
        query = input(">")
        if query.lower() in ["exit", "quit", "q", "e", "bye", "goodbye", "bye"]:
            break

        if query == "/clear":
            message_history = None
            continue

        response = agent.run_sync(query, deps=AgentDeps(database=database), message_history=message_history)
        console.print(Markdown(response.data))
        message_history = response.all_messages()


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
        help="Name of the LLM model to use, in format provider:model (e.g. openai:gpt-4o). Choices (not exhaustive, more may be supported):\n"
        + format_model_options(MODEL_OPTIONS),
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
