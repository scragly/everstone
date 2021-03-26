from __future__ import annotations

import typing as t

from . import table as tbl
from ..bases import LimitInstances

if t.TYPE_CHECKING:
    from everstone.database import Database


class Schema(LimitInstances):
    """Represents a database schema."""

    def __init__(self, name: str, database: Database):
        self.name = name
        self.db: Database = database
        self.tables: t.Set[tbl.Table] = set()
        self._exists = None

    def __repr__(self):
        return f"<Schema '{self.name}' on '{self.db.name}'>"

    def __str__(self):
        return self.name

    async def prepare(self):
        """Ensure the schema exists in the database and prepare all child tables."""
        await self.create(if_exists=False)
        for table in self.tables:
            await table.prepare()

    @property
    def exists(self) -> t.Optional[bool]:
        """Returns True if Schema created or False if Schema dropped."""
        return self._exists

    def add_table(self, table: tbl.Table) -> Schema:
        """Add a table under this schema."""
        self.tables.add(table)
        return self

    async def rename(self, name: str) -> str:
        """Alter the name of this schema."""
        sql = f"ALTER SCHEMA {self.name} RENAME TO $1"
        result = await self.db.execute(sql, name)
        del self.__instances__[self.name]
        self.__instances__[name] = self
        return result

    async def create(self, *, if_exists: bool = True) -> str:
        """Create the schema on the database."""
        if if_exists:
            sql = f"CREATE SCHEMA {self.name};"
        else:
            sql = f"CREATE SCHEMA IF NOT EXISTS {self.name};"
        results = await self.db.execute(sql)
        self._exists = True
        return results

    async def drop(self, *, if_exists: bool = False, cascade: bool = False) -> str:
        """Drop the schema from the database."""
        exists = "IF EXISTS " if if_exists else ""
        cascade = " CASCADE" if cascade else ""
        sql = f"DROP SCHEMA {exists}{self.name}{cascade};"
        results = await self.db.execute(sql)
        self._exists = False
        return results

    def Table(self, name: str) -> tbl.Table:
        """Return a Table isntance bound to this Schema."""
        return tbl.Table(name, self)
