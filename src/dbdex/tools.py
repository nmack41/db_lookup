from typing import Any

from pydantic import BaseModel
from pydantic_ai import ModelRetry, RunContext
from rich.markdown import Markdown

from dbdex.database import InvalidQueryError
from dbdex.deps import AgentDeps, CLIAgentDeps


class DBQueryResponse(BaseModel):
    """Result of a database query"""

    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    note: str | None = None


def execute_sql(ctx: RunContext[AgentDeps], sql: str) -> DBQueryResponse:
    """Execute the given SQL query and return the result in format:
    ```json
    {
        "columns": ["column1", "column2", ...],
        "rows": [[row1_value1, row1_value2, ...], [row2_value1, row2_value2, ...], ...],
        "note": "Optional note about the query"
    }
    ```
    The results may be truncated if they contain lots of data."""
    try:
        result = ctx.deps.database.execute_sql(sql)
    except InvalidQueryError as e:
        raise ModelRetry(str(e)) from e

    if not result.rows:
        return DBQueryResponse(note="No results")
    else:
        assert result.columns is not None
        # Calculate number of rows to return
        max_return_rows = 5 + ctx.deps.max_return_values // len(result.columns)
        rows = [list(row) for row in result.rows[:max_return_rows]]
        note = None
        if len(result.rows) > max_return_rows:
            note = f"Query returned {len(result.rows)} rows, showing first {max_return_rows} only"
        return DBQueryResponse(columns=result.columns, rows=rows, note=note)


def show_result_table(ctx: RunContext[CLIAgentDeps]) -> str:
    """Display the entire result of the previous database query as a markdown table.
    (Not just the first X rows that were returned by the *execute_sql* tool.)
    Call this tool instead of formatting the data as a table in your response."""
    result = ctx.deps.database.last_query
    if not result:
        return "No previous query results."
    ctx.deps.console.print(Markdown(result.to_markdown(include_details=False)))
    return "Result displayed, DO NOT also provide the result data in your response."
