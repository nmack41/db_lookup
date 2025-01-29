from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
from pydantic_ai.result import RunResult

from dbdex.database import Database
from dbdex.deps import AgentDeps
from dbdex.tools import execute_sql, show_result_table

DepsT = TypeVar("DepsT", bound=AgentDeps)


@dataclass
class AgentRunner(Generic[DepsT]):
    """
    Class which wraps an Agent to facilitate agent execution by:
    - Maintaining and managing message history
    - Providing dependenices
    """

    agent: Agent[DepsT, str]
    deps: DepsT
    message_history: list[ModelMessage] | None = None

    def clear_message_history(self) -> None:
        """Clear the message history."""
        self.message_history = None

    def run_sync(self, query: str) -> RunResult[str]:
        """Run a query and automatically provide dependencies and message history."""
        response = self.agent.run_sync(query, deps=self.deps, message_history=self.message_history)
        self.message_history = response.all_messages()
        return response


def get_agent_runner(model: Model, deps: DepsT) -> AgentRunner[DepsT]:
    agent = Agent(
        model=model,
        deps_type=type(deps),
        system_prompt=get_system_prompt(deps.database),
        tools=[execute_sql, show_result_table],
    )
    return AgentRunner(agent, deps=deps)


PROMPT_TEMPLATE = """
# IDENTITY AND PURPOSE

You are a helpful assistant and database and SQL expert that can answer questions about the data and
 schema of a *{database_provider}* database which you have access to execute SQL queries on.

# IMPORTANT RULES AND EXPECTED BEHAVIOUR

* If the user request is unclear, ambigious or invalid, ask clarifying questions.
* If you need to query the database for new information to answer the user's question,
 determine the pprioriate SQL and *EXECUTE IT* using the *execute_sql* tool.
* Always execute the query to retrieve data instead of just returning the SQL statement,
 unless explicitly asked to do otherwise.
* You are only allowed to perform SELECT style queries (no INSERT, UPDATE, DELETE, etc).
* Try to avoid database queries where possible if the data is already available from a previous query.
* Use Markdown formatting to make the output more readable when necessary.
* To display the result of a previous query, call the *show_result_table* tool instead of formatting the data as a table
 in your response.
* If *show_result_table* tool is called, do not also format the data as a table in your response.

# EXAMPLES

GOOD:
User: What is the total revenue for each product category?
Assistant: Let me query that for you! <Uses execute_sql() to run query>
User: <responds with the result of the query>
Assistant: I've dispalyed the results of the query. <uses show_result_table() to display the result>

GOOD:
User: Can you show me the SQL query to count users by month?
Assistant: Here's the SQL query:
```sql
SELECT DATE_TRUNC('month', created_at) as month, COUNT(*)
FROM users
GROUP BY 1
```

BAD:
User: What is the total revenue for each product category?
Assistant: SELECT SUM(revenue) FROM products GROUP BY category;

BAD:
User: Show all customer records
Assistant: Let me query that for you! <Uses execute_sql() to run query>
User: <responds with the result of the query>
Assistant: Here are the results: <includes result data formatted as table in response>

# Database Schema
{database_schema}
"""


def get_system_prompt(database: Database) -> str:
    return PROMPT_TEMPLATE.format(database_provider=database.provider, database_schema=database.describe_schema())
