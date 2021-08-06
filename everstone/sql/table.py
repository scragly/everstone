from __future__ import annotations

import contextlib
import typing as t

from . import aggregates, column, select
from .. import database
from ..exceptions import SchemaError

if t.TYPE_CHECKING:
    from .constraints import Constraint
    from .schema import Schema
    from .types import SQLType


class Columns:
    def __init__(self, table: Table):
        self.table: Table = table
        self._columns: t.Dict[str, column.Column] = dict()

    def __bool__(self):
        return bool(self._columns)

    def __len__(self):
        return len(self._columns)

    def __iter__(self):
        return iter(self._columns.values())

    def __getitem__(self, item: str) -> column.Column:
        return self._columns[item]

    def __setitem__(self, key: str, value: column.Column):
        self._columns[key] = value

    def __getattr__(self, item) -> column.Column:
        with contextlib.suppress(KeyError):
            return self._columns[item]
        raise AttributeError(f"Column '{item}' not found on '{self.table}'.")


class Table:
    """Represents an SQL table."""

    def __init__(self, name: str, schema: t.Union[Schema, database.Database]):
        self.name = name

        if isinstance(schema, database.Database):
            self.db: database.Database = schema
            self.schema: Schema = self.db.public_schema
        else:
            self.db: database.Database = schema.db
            self.schema: Schema = schema

        self.schema.add_table(self)

        self.columns: Columns = Columns(self)
        self.constraints: t.Set[Constraint] = set()

    @property
    def full_name(self) -> str:
        """Return the fully qualified name of the current table."""
        return f"{self.schema}.{self.name}"

    @property
    def count(self) -> aggregates.Count:
        """Returns an aggregate representing count(*) for this table."""
        return aggregates.Count(self)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        if self.columns:
            cols = ", ".join(c.name for c in self.columns)
            return f"<Table {self.full_name} ({cols})>"
        return f"<Table {self.full_name}>"

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
        cols = [col.definition for col in self.columns]
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

    def Column(self, name: str, type: SQLType, *constraints: Constraint) -> Column:
        """Return a Column instance bound to this table."""
        col = column.Column(name, type, *constraints).bind_table(self)
        self.columns[col.name] = col
        return col

    def select(self, *columns: Column) -> select.Select:
        """Begin a select query for this table."""
        return select.Select(self.db).select(*columns)
