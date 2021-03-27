from __future__ import annotations

import typing as t

from . import aggregates, comparisons

if t.TYPE_CHECKING:
    from .constraints import Constraints
    from .types import SQLTypes
    from .table import Table


class Column(comparisons.Comparable):
    """Reprents an SQL column."""

    def __init__(self, name: str, type: SQLTypes, constraint: t.Optional[Constraints] = None):
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

    @property
    def full_name(self) -> str:
        """Return the fully qualified name for the column."""
        if self.table:
            return f"{self.table.name}.{self.name}"
        else:
            return self.name

    def bind_table(self, table: Table) -> Column:
        """Binds a table to this column."""
        self.table = table
        return self

    # region: meta

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.full_name} {self.type}>"

    # endregion

    # region: aggregates

    @property
    def avg(self) -> aggregates.Avg:
        """Return the avg aggregate for this column."""
        return aggregates.Avg(self).as_("avg")

    @property
    def bit_and(self) -> aggregates:
        """Return the bit_and aggregate for this column."""
        return aggregates.Avg(self).as_("bit_and")

    @property
    def bit_or(self) -> aggregates:
        """Return the bit_or aggregate for this column."""
        return aggregates.Avg(self).as_("bit_or")

    @property
    def bool_and(self) -> aggregates:
        """Return the bool_and aggregate for this column."""
        return aggregates.Avg(self).as_("bool_and")

    @property
    def bool_or(self) -> aggregates:
        """Return the bool_or aggregate for this column."""
        return aggregates.Avg(self).as_("bool_or")

    @property
    def count(self) -> aggregates.Count:
        """Return the count aggregate for this column."""
        return aggregates.Count(self).as_("count")

    @property
    def max(self) -> aggregates.Max:
        """Return the max aggregate for this column."""
        return aggregates.Max(self).as_("max")

    @property
    def min(self) -> aggregates.Min:
        """Return the min aggregate for this column."""
        return aggregates.Min(self).as_("min")

    @property
    def sum(self) -> aggregates.Sum:
        """Return the sum aggregate for this column."""
        return aggregates.Sum(self).as_("sum")

    # endregion
