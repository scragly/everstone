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
        self._default = None

    @property
    def default(self) -> t.Any:
        """Default for the column."""
        return self._default

    @property
    def definition(self) -> str:
        """SQL definition for this column."""
        sql = f"{self.name} {self.type}"
        if self.constraint:
            sql += f" {self.constraint}"
        return sql

    @property
    def full_name(self) -> str:
        """Fully qualified name for the column."""
        if self.table:
            return f"{self.table.name}.{self.name}"
        else:
            return self.name

    def bind_table(self, table: Table) -> Column:
        """Bind the given table to this column."""
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
        """Average of all non-null values in this column."""
        return aggregates.Avg(self).as_("avg")

    @property
    def bit_and(self) -> aggregates:
        """Bitwise AND of all non-null values in this column."""
        return aggregates.Avg(self).as_("bit_and")

    @property
    def bit_or(self) -> aggregates:
        """Bitwise OR of all non-null values in this column."""
        return aggregates.Avg(self).as_("bit_or")

    @property
    def bool_and(self) -> aggregates:
        """Returns True if ALL non-null values in this column are True."""
        return aggregates.Avg(self).as_("bool_and")

    @property
    def bool_or(self) -> aggregates:
        """Returns True if ANY non-null values in this column are True."""
        return aggregates.Avg(self).as_("bool_or")

    @property
    def count(self) -> aggregates.Count:
        """Counts of all rows."""
        return aggregates.Count(self).as_("count")

    @property
    def max(self) -> aggregates.Max:
        """Maximum of all non-null values in this column."""
        return aggregates.Max(self).as_("max")

    @property
    def min(self) -> aggregates.Min:
        """Minimum of all non-null values in this column."""
        return aggregates.Min(self).as_("min")

    @property
    def sum(self) -> aggregates.Sum:
        """Sum of all non-null values in this column."""
        return aggregates.Sum(self).as_("sum")

    # endregion
