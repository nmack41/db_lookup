import time
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic_ai import Agent, UnexpectedModelBehavior
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import KnownModelName
from pydantic_ai.result import RunResult

from chatdb.database import Database
from chatdb.deps import CLIAgentDeps
from chatdb.llm import build_model_from_name_and_api_key
from chatdb.tools import execute_sql, show_result_table

T = TypeVar("T")


@dataclass
class AgentRunner(Generic[T]):
    """
    Class which wraps an Agent to facilitate agent execution by:
    - Automatically retrying on API overload
    - Maintaining and managing message history
    - Providing dependenices
    """

    agent: Agent[T, str]
    deps: T
    message_history: list[ModelMessage] | None = None

    def clear_message_history(self) -> None:
        """Clear the message history."""
        self.message_history = None

    def run_sync(self, query: str, max_retries: int = 3) -> RunResult[str]:
        """Run a query with automatic retries on overload."""
        retries = 0
        while retries < max_retries:
            try:
                response = self.agent.run_sync(query, deps=self.deps, message_history=self.message_history)
                self.message_history = response.all_messages()
                return response
            except UnexpectedModelBehavior as e:
                if "503" in str(e) and "overloaded" in str(e):
                    retries += 1
                    if retries < max_retries:
                        time.sleep(0.1)  # Wait 100ms before retry
                        continue
                raise


def get_agent_runner(model_name: KnownModelName, api_key: str, deps: CLIAgentDeps) -> AgentRunner[CLIAgentDeps]:
    model = build_model_from_name_and_api_key(model_name, api_key)

    agent = Agent(
        model=model,
        deps_type=CLIAgentDeps,
        system_prompt=get_system_prompt(deps.database),
        tools=[execute_sql, show_result_table],
    )
    return AgentRunner(agent, deps=deps)


def get_system_prompt(database: Database) -> str:
    database_schema = database.describe_schema()

    return (
        f"You are a helpful assistant and database and SQL expert that can answer questions about the data and "
        f"schema of a *{database.provider}* database which you have access to execute SQL queries on. \n\n"
        "# Important Rules\n"
        "* If the user request is unclear, ambigious or invalid, ask clarifying questions. \n"
        "* If you need to query the database for new information to answer the user's question, determine the "
        "apprioriate SQL and execute it using the *execute_sql* tool. "
        "* Always execute the query to retrieve data instead of just returning the SQL statement, "
        "unless explicitly asked to do otherwise. \n"
        "* You are only allowed to perform SELECT style queries (no INSERT, UPDATE, DELETE, etc). \n"
        "* Try to avoid database queries where possible if the data is already available from a previous query. \n"
        "* Use Markdown formatting to make the output more readable when necessary. \n"
        "* To display the result of a previous query, call the *show_result_table* tool instead of "
        "formatting the data as a table in your response. If *show_result_table* tool is called, do not also "
        "format the data as a table in your response. \n\n"
        f"# Database Schema \n{database_schema}"
    )
