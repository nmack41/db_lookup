from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import KnownModelName

from chatdb.database import Database, format_table_schema
from chatdb.models import build_model_from_name_and_api_key


@dataclass
class AgentDeps:
    database: Database


def get_agent(model_name: KnownModelName, api_key: str, database: Database) -> Agent[AgentDeps, str]:
    model = build_model_from_name_and_api_key(model_name, api_key)

    agent = Agent(model=model, deps_type=AgentDeps, system_prompt=get_system_prompt(database), tools=[execute_sql])
    return agent


def get_system_prompt(database: Database) -> str:
    tables = database.get_tables()
    database_schema = "\n\n".join([format_table_schema(table) for table in tables])

    return (
        f"You are a helpful assistant and database and SQL expert that can answer questions about the data and "
        f"schema of a *{database.provider}* database. \n"
        "If the user request is unclear, ambigious or invalid, ask clarifying questions. \n"
        "If you need to query the database for new information to answer the user's question, determine the "
        "apprioriate SQL and execute it using the *execute_sql* tool. \n"
        "Try to avoid database queries where possible if the data is already available from a previous query. \n"
        "Use Markdown formatting to make the output more readable when necessary. \n"
        f"The database schema is: \n{database_schema}"
    )


class DBQueryResult(BaseModel):
    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    notes: str | None = None


def execute_sql(ctx: RunContext[AgentDeps], sql: str) -> DBQueryResult:
    """Execute the given SQL query and return the result."""
    rows = ctx.deps.database.execute_query(sql)
    if not rows:
        return DBQueryResult(notes="No results")
    else:
        return DBQueryResult(columns=rows[0]._fields, rows=[list(row) for row in rows])
