from dataclasses import dataclass
from datetime import datetime, timedelta

import logfire
from sqlalchemy import (
    MetaData,
    Row,
    Table,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.sql.schema import ForeignKeyConstraint


@dataclass
class QueryResult:
    """Container for SQL query and its results."""

    sql: str
    rows: list[Row]
    executed_at: datetime
    duration: timedelta | None = None
    error: Exception | None = None

    @property
    def success(self) -> bool:
        return self.error is None

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def columns(self) -> list[str] | None:
        """Get column names if there are results."""
        if self.rows:
            return list(self.rows[0]._fields)
        return None

    def to_markdown(self, include_sql: bool = True) -> str:
        """Format query results as a markdown table."""
        md = ""
        if include_sql:
            md += f"```sql\n{self.sql}\n```\n\n"

        if self.error:
            md += f"❌ Error: {str(self.error)}\n"
            return md

        duration_str = f"{self.duration.total_seconds():.3f}s" if self.duration else "unknown"
        md += f"✓ Executed in {duration_str}\n\n"

        if not self.rows or not self.columns:
            md += "No results"
            return md

        # Build results table
        md += "| " + " | ".join(self.columns) + " |\n"
        md += "|" + "|".join(["---"] * len(self.columns)) + "|\n"

        # Add data rows
        for row in self.rows:
            values = [str(val) if val is not None else "" for val in row]
            md += "| " + " | ".join(values) + " |\n"

        return md


class InvalidQueryError(Exception):
    """Exception raised for invalid SQL queries."""


class TableNotFoundError(Exception):
    """Exception raised for invalid table names."""


class Database:
    """A class to interact with a SQL database using SQLAlchemy."""

    def __init__(self, db_uri: str):
        """Initialize database connection and reflect schema.

        Args:
            db_uri: SQLAlchemy connection string for the database
        """
        self.engine = create_engine(db_uri)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.last_query: QueryResult | None = None
        logfire.instrument_sqlalchemy(engine=self.engine)

    @property
    def provider(self) -> str:
        return self.engine.dialect.name

    def execute_sql(self, sql_query: str) -> QueryResult:
        """Execute a SQL query and return results. Only allows SELECT style queries.

        Args:
            query: SQL query string to execute

        Returns:
            List of dictionaries containing query results
        """
        if not sql_query.strip().startswith("SELECT"):
            raise InvalidQueryError("Only SELECT style queries are allowed")

        result = QueryResult(
            sql=sql_query,
            rows=[],
            executed_at=datetime.now(),
        )

        with self.engine.connect() as conn:
            try:
                start_time = datetime.now()
                sql_result = conn.execute(text(sql_query))
                if sql_result.returns_rows:
                    result.rows = list(sql_result)
                else:
                    result.rows = []
            except Exception as e:
                result.error = e
                raise
            finally:
                result.duration = datetime.now() - start_time
                self.last_query = result

        return result

    @property
    def table_names(self) -> list[str]:
        return list(self.metadata.tables.keys())

    def get_tables(self) -> list[Table]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        return list(self.metadata.tables.values())

    def describe_schema(self, table_names: list[str] | None = None) -> str:
        """Get a sring representation of the structure of tables in the database (all by default)"""
        if table_names:
            try:
                tables = [self.metadata.tables[table] for table in table_names]
            except KeyError as e:
                raise TableNotFoundError(f"Invalid table name: {e}") from e
        else:
            tables = self.get_tables()
        return "\n\n".join(format_table_schema(table) for table in tables)


def format_table_schema(table: Table) -> str:
    """
    Formats a SQLAlchemy Table object into a schema string representation like:
    TABLE table_name (
        COLUMNS
            column_name column_type [PRIMARY KEY] [NOT NULL] [DEFAULT value]
        INDEXES
            INDEX index_name (column_name [ASC|DESC])
        CONSTRAINTS
            FOREIGN KEY (column_name) REFERENCES target_table (target_column)
    )
    """

    schema_lines = [f"TABLE {table.name} ("]

    # Format column definitions
    schema_lines.append("    COLUMNS")
    for column in table.columns:
        column_definition = f"        {column.name} {column.type}"
        if column.primary_key:
            column_definition += " PRIMARY KEY"
        if not column.nullable:
            column_definition += " NOT NULL"
        if column.default:
            column_definition += f" DEFAULT {column.default.arg}"  # type: ignore
        if column.unique:
            column_definition += " UNIQUE"
        schema_lines.append(column_definition + ",")

    schema_lines.append("    ---")

    # Format indexes
    schema_lines.append("    INDEXES")
    for index in table.indexes:
        index_columns = []
        for column in index.columns:
            if (
                index.dialect_options.get("postgresql_using", "") == "gin"
                or index.dialect_options.get("postgresql_using", "") == "gist"
            ):
                index_columns.append(f"{column.name}")
            elif column.name in index.kwargs.get("descending_cols", []):
                index_columns.append(f"{column.name} DESC")
            else:
                index_columns.append(f"{column.name} ASC")
        index_columns_str = ", ".join(index_columns)
        schema_lines.append(f"        INDEX {index.name} ({index_columns_str}),")

    schema_lines.append("    ---")

    # Format constraints
    schema_lines.append("    CONSTRAINTS")

    # Format foreign keys
    for fk_constraint in table.constraints:
        if isinstance(fk_constraint, ForeignKeyConstraint):
            for fk in fk_constraint.elements:
                schema_lines.append(
                    f"        FOREIGN KEY ({fk.parent.name}) REFERENCES {fk.column.table.name} ({fk.column.name}),"
                )

    # Format unique constraints (if not already handled inline)
    for unique_constraint in table.constraints:
        if isinstance(unique_constraint, UniqueConstraint):
            uc_cols = ", ".join(uc_col.name for uc_col in unique_constraint.columns)
            schema_lines.append(f"        UNIQUE ({uc_cols}),")

    # Remove trailing comma from the last line in each section
    sections = ["COLUMNS", "INDEXES", "CONSTRAINTS"]
    for i in range(len(schema_lines) - 1, 0, -1):
        line = schema_lines[i].strip()
        if line.startswith("---"):
            continue
        if any(line.startswith(section) for section in sections):
            continue
        if schema_lines[i].endswith(","):
            schema_lines[i] = schema_lines[i].rstrip(",")
            break

    schema_lines.append(")")
    return "\n".join(schema_lines)
