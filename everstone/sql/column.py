from __future__ import annotations

import typing as t

from . import aggregates, comparisons

if t.TYPE_CHECKING:
    from .constraints import Constraint
    from .types import SQLType
    from .table import Table


class Column(comparisons.Comparable):
    """Reprents an SQL column."""

    def __init__(self, name: str, type: SQLType, constraint: t.Optional[Constraint] = None):
        self.name = name
        self.type = type
        self.constraint = constraint
        self.table: t.Optional[Table] = None

    @property
    def definition(self) -> str:
        """Return the SQL definition for this column."""
        sql = f"{self.name} {self.type}"
        if self.constraint:
            sql += f" {self.constraint}"
        return sql

    def bind_table(self, table: Table) -> Column:
        """Binds a table to this column."""
        self.table = table
        return self

    def __str__(self) -> str:
        if self.table:
            return f"{self.table}.{self.name}"
        else:
            return self.name

    @property
    def avg(self) -> aggregates.Avg:
        """Return the avg aggreate for this column."""
        return aggregates.Avg(self)

    @property
    def count(self) -> aggregates.Count:
        """Return the count aggreate for this column."""
        return aggregates.Count(self)

    @property
    def max(self) -> aggregates.Max:
        """Return the max aggreate for this column."""
        return aggregates.Max(self)

    @property
    def min(self) -> aggregates.Min:
        """Return the min aggreate for this column."""
        return aggregates.Min(self)

    @property
    def sum(self) -> aggregates.Sum:
        """Return the sum aggreate for this column."""
        return aggregates.Sum(self)
