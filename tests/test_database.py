from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy.engine import Row

from chatdb.database import QueryResult


def make_rows(data: list[dict[str, Any]]) -> list[Row[Any]]:
    """Create a SQLAlchemy Row with the given values."""
    if not data:
        return []

    FakeRow = namedtuple("FakeRow", data[0].keys())  # type: ignore[no-redef]
    return [cast(Row[Any], FakeRow(**row)) for row in data]


class TestQueryResult:
    def test_query_result_to_markdown_with_results(self) -> None:
        """Test formatting query results as markdown."""
        result = QueryResult(
            sql="SELECT id, name FROM users",
            rows=make_rows([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]),
            executed_at=datetime(2024, 1, 1),
            duration=timedelta(seconds=0.123),
        )

        expected = (
            "```sql\n"
            "SELECT id, name FROM users\n"
            "```\n"
            "\n"
            "✓ Executed in 0.123s\n"
            "\n"
            "| id | name |\n"
            "|---|---|\n"
            "| 1 | Alice |\n"
            "| 2 | Bob |\n"
        )
        assert result.to_markdown() == expected

        # Test with include_sql=False
        expected_no_sql = "| id | name |\n|---|---|\n| 1 | Alice |\n| 2 | Bob |\n"
        assert result.to_markdown(include_details=False) == expected_no_sql

    def test_query_result_to_markdown_with_error(self) -> None:
        """Test formatting query results with error as markdown."""
        result = QueryResult(
            sql="SELECT bad syntax",
            rows=[],
            executed_at=datetime(2024, 1, 1),
            error=Exception("Syntax error"),
        )

        expected = "```sql\nSELECT bad syntax\n```\n\n❌ Error: Syntax error\n"
        assert result.to_markdown() == expected

    def test_query_result_to_markdown_no_results(self) -> None:
        """Test formatting empty query results as markdown."""
        result = QueryResult(
            sql="SELECT * FROM empty_table",
            rows=[],
            executed_at=datetime(2024, 1, 1),
            duration=timedelta(seconds=0.001),
        )

        expected = "```sql\nSELECT * FROM empty_table\n```\n\n✓ Executed in 0.001s\n\nNo results"
        assert result.to_markdown() == expected

    def test_query_result_to_csv_with_results(self) -> None:
        """Test formatting query results as CSV."""
        result = QueryResult(
            sql="SELECT id, name, age FROM users",
            rows=make_rows(
                [
                    {"id": 1, "name": "Alice", "age": 30},
                    {"id": 2, "name": "Bob", "age": 25},
                    {"id": 3, "name": "Charlie", "age": None},  # Test NULL/None value
                ]
            ),
            executed_at=datetime(2024, 1, 1),
        )

        csv_data = result.to_csv()
        expected = "id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,\n"  # Empty value for None
        assert csv_data == expected

    def test_query_result_to_csv_no_results(self) -> None:
        """Test formatting empty query results as CSV."""
        result = QueryResult(
            sql="SELECT * FROM empty_table",
            rows=[],
            executed_at=datetime(2024, 1, 1),
        )

        assert result.to_csv() == ""

    def test_query_result_properties(self) -> None:
        """Test QueryResult property methods."""
        result = QueryResult(
            sql="SELECT id, name FROM users",
            rows=make_rows(
                [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"},
                ]
            ),
            executed_at=datetime(2024, 1, 1),
        )

        assert result.success is True
        assert result.row_count == 2
        assert result.columns == ["id", "name"]

        # Test with error
        error_result = QueryResult(
            sql="SELECT bad syntax",
            rows=[],
            executed_at=datetime(2024, 1, 1),
            error=Exception("Syntax error"),
        )

        assert error_result.success is False
        assert error_result.row_count == 0
        assert error_result.columns is None
