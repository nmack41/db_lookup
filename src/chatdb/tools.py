from typing import Any

from pydantic import BaseModel
from pydantic_ai import RunContext
from rich.markdown import Markdown

from chatdb.deps import AgentDeps


class DBQueryResponse(BaseModel):
    """Result of a database query, to provide to the LLM"""

    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    note: str | None = None


def execute_sql(ctx: RunContext[AgentDeps], sql: str) -> DBQueryResponse:
    """Execute the given SQL query and return the result."""
    result = ctx.deps.database.execute_query(sql)
    if not result.rows:
        return DBQueryResponse(note="No results")
    else:
        rows = [list(row) for row in result.rows[: ctx.deps.max_rows]]
        notes = None
        if len(result.rows) > ctx.deps.max_rows:
            notes = f"Query returned {len(result.rows)} rows, showing first {ctx.deps.max_rows} only"
        return DBQueryResponse(columns=result.columns, rows=rows, note=notes)


def show_result_table(ctx: RunContext[AgentDeps]) -> str:
    """Display the result of the previous database query as a markdown table."""
    result = ctx.deps.database.last_query
    if not result:
        return "No previous query results."
    ctx.deps.console.print(Markdown(result.to_markdown(include_sql=False)))
    return "Result displayed."
