from __future__ import annotations

import typing as t

from . import column
from .. import database

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

    @property
    def full_name(self) -> str:
        """Return the fully qualified name of the current table."""
        return f"{self.schema}.{self.name}"

    def __str__(self):
        return self.full_name

    def __hash__(self):
        return hash(self.full_name)

    def __eq__(self, other: t.Any):
        if isinstance(other, Table):
            return self.full_name == other.full_name
        return False

    async def prepare(self):
        """Ensure the table exists in the database."""
        await self.create(if_exists=False)

    async def create(self, if_exists: bool = False):
        """Create the table in the database."""
        pass

    async def drop(self):
        """Drop table from database."""
        sql = "DROP TABLE $1"
        await self.db.execute(sql, self.full_name)

    def Column(self, name: str, type: SQLType, constraint: t.Optional[Constraint] = None) -> Column:
        """Return a Column instance bound to this table."""
        return column.Column(name, type, constraint).bind_table(self)
