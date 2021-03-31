from __future__ import annotations

import typing as t

from .. import database

if t.TYPE_CHECKING:
    from .column import Column
    from .table import Table


class Select:
    def __init__(self, db: database.Database = None):
        self.db = db or database.Database.get_default()

        # references
        self._columns: t.List[Column] = []

        # modifiers
        self._distinct = False
        self._grouped = []
        self._ordered = []

    def select(self, *columns: Column) -> Select:
        self._columns.extend(columns)
        return self

    @property
    def columns(self) -> t.Tuple[Column, ...]:
        return tuple(self._columns)

    def __call__(self, *columns: Column, distinct=None):
        if distinct is not None:
            self._distinct = distinct
        self._columns.extend(columns)

    @property
    def _tables(self) -> t.Set[Table]:
        return {c.table for c in self._columns}

    @property
    def _column_str(self) -> str:
        return ", ".join(str(c) for c in self._columns)

    @property
    def _table_str(self) -> str:
        return ", ".join(str(tbl) for tbl in self._tables)

    @property
    def distinct(self) -> Select:
        self._distinct = True
        return self

    def __str__(self):
        if not self._columns:
            return "SELECT NULL"

        sql = f"SELECT {self._column_str}"
        if self._tables:
            sql += f" FROM {self._table_str}"
        return sql

    def __repr__(self):
        return f"<Query '{self}'>"
