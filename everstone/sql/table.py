from __future__ import annotations

import typing as t

from . import column
from .. import database
from ..exceptions import SchemaError

if t.TYPE_CHECKING:
    from .constraints import Constraint
    from .schema import Schema
    from .types import SQLType


class Table:
    """Represents an SQL table."""

    def __init__(self, name: str, schema: t.Union[Schema, database.Database]):
        self.name = name

        if isinstance(schema, database.Database):
            self.db: database.Database = schema
            self.schema: Schema = self.db.Schema("public")
        else:
            self.db: database.Database = schema.db
            self.schema: Schema = schema

        self.schema.add_table(self)

        self.columns: t.Dict[str, column.Column] = dict()
        self.constraints: t.Set[Constraint] = set()

    @property
    def full_name(self) -> str:
        """Return the fully qualified name of the current table."""
        return f"{self.schema}.{self.name}"

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<Table '{self.full_name}'>"

    def __hash__(self):
        return hash(self.full_name)

    def __eq__(self, other: t.Any):
        if isinstance(other, Table):
            return self.full_name == other.full_name
        return False

    def add_columns(self, *columns: column.Column) -> Table:
        """Add columns to the current table."""
        for c in columns:
            c.bind_table(self)
            self.columns[c.name] = c
        return self

    def add_constraints(self, *constraints: Constraint):
        for c in constraints:
            self.constraints.add(c)

    async def prepare(self):
        """Ensure the table exists in the database."""
        await self.create(if_not_exists=True)

    async def create(self, if_not_exists: bool = False) -> str:
        """Create the table in the database."""
        if not self.columns:
            raise SchemaError("Table creation failed: No columns.")
        exists = "IF NOT EXISTS " if if_not_exists else ""
        cols = [col.definition for col in self.columns.values()]
        constraints = [con.sql for con in self.constraints]
        schema = ", ".join(cols + constraints)
        sql = f"CREATE TABLE {exists}{self.name} ({schema});"
        return await self.db.execute(sql)

    async def drop(self, if_exists: bool = False, cascade: bool = False) -> str:
        """Drop the table from the database."""
        exists = "IF EXISTS " if if_exists else ""
        cascade = " CASCADE" if cascade else ""
        sql = f"DROP TABLE {exists}{self.name}{cascade};"
        return await self.db.execute(sql)

    def Column(self, name: str, type: SQLType, constraint: t.Optional[Constraint] = None) -> Column:
        """Return a Column instance bound to this table."""
        col = column.Column(name, type, constraint).bind_table(self)
        self.columns[col.name] = col
        return col
