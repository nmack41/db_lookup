from dataclasses import dataclass

from rich.console import Console

from chatdb.database import Database


@dataclass
class AgentDeps:
    database: Database
    console: Console
    # Maximum number of DB result rows to show the LLM
    max_rows: int = 20
