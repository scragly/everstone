from __future__ import annotations

import typing as t

from . import where
from .. import database

if t.TYPE_CHECKING:
    from .aggregates import Aggregate
    from .column import Column
    from .table import Table


class Select:
    def __init__(self, db: database.Database = None):
        self.db = db or database.Database.get_default()
        self.where = where.Where(self)

        # references
        self._columns: t.List[t.Union[Column, Aggregate]] = []

        # modifiers
        self._distinct: t.Union[bool, tuple[Column, ...]] = False
        self._grouped = []
        self._ordered: t.Dict[Column, str] = dict()
        self._conditions = []
        self._having = []

    def select(self, *columns: Column) -> Select:
        self._columns.extend(columns)
        return self

    def new(self) -> Select:
        return Select(self.db)

    @property
    def columns(self) -> t.Tuple[Column, ...]:
        return tuple(self._columns)

    @property
    def sql(self):
        if not self._columns:
            return "SELECT NULL"

        if self._distinct is True:
            sql = f"SELECT DISTINCT {self._column_str}"
        elif self._distinct is not False:
            d_on = ", ".join((str(c) for c in self._distinct))
            sql = f"SELECT DISTINCT ON ({d_on}) {self._column_str}"
        else:
            sql = f"SELECT {self._column_str}"

        if self._tables:
            sql += f" FROM {self._table_str}"

        if self._grouped:
            cols = ", ".join(str(c) for c in self._grouped)
            sql += f" GROUP BY {cols}"

        return f"{sql};"

    def __call__(self, *columns: Column) -> Select:
        return self.new().select(*columns)

    def __await__(self):
        return self.db.execute(self.sql).__await__()

    def group_by(self, *columns):
        self._grouped = list(columns)

    @property
    def groups(self) -> t.List[Column]:
        return self._grouped

    @property
    def _tables(self) -> t.Set[Table]:
        return {c.table for c in self._columns if not isinstance(c, str) and c.table}

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

    def distinct_on(self, *columns) -> Select:
        for col in columns:
            if col not in set(self._columns):
                self._columns.append(col)
        self._distinct = columns
        return self

    def __str__(self):
        return self.sql

    def __repr__(self):
        return f"<Select '{self}'>"
