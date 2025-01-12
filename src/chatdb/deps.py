from dataclasses import dataclass

from rich.console import Console

from chatdb.database import Database


@dataclass
class AgentDeps:
    database: Database
    # Maximum number of DB result values (rows X columns) to return to the LLM
    max_return_values: int


@dataclass
class CLIAgentDeps(AgentDeps):
    console: Console
