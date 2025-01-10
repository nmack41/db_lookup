from sqlalchemy import (
    MetaData,
    Row,
    Table,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.sql.schema import ForeignKeyConstraint


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

    @property
    def provider(self) -> str:
        return self.engine.dialect.name

    def execute_query(self, query: str) -> list[Row]:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string to execute

        Returns:
            List of dictionaries containing query results
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            if result.returns_rows:
                return list(result)
            else:
                return []

    def get_tables(self) -> list[Table]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        return list(self.metadata.tables.values())


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
            column_definition += f" DEFAULT {column.default.arg}"
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
