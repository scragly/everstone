from __future__ import annotations

import typing as t

from . import aggregates, comparisons
from .. import exceptions

if t.TYPE_CHECKING:
    from .constraints import Constraints
    from .types import SQLTypes
    from .table import Table


class DefaultNotSet:
    pass


class Column(comparisons.Comparable):
    """Reprents an SQL column."""

    def __init__(self, name: str, type: SQLTypes, *constraints_: Constraints, default=DefaultNotSet):
        self._name = name
        self.type = type
        self.constraints = set(constraints_) if constraints_ else set()
        self.alias: t.Optional[str] = None
        self.table: t.Optional[Table] = None
        self._default = default

        # query modifiers
        self._sort_direction = None
        self._grouped = False

    @property
    def name(self) -> str:
        return self.alias or self._name

    @property
    def sort_direction(self) -> t.Optional[str]:
        return self._sort_direction

    @property
    def grouped(self):
        self._grouped = True
        return self

    def reset_modifiers(self):
        self._sort_direction = None
        self._grouped = False

    @property
    def default(self) -> t.Any:
        """Default for the column."""
        if self._default is DefaultNotSet:
            raise exceptions.SchemaError("No default is set for this column.")
        return self._default

    @property
    def definition(self) -> str:
        """SQL definition for this column."""
        sql = f"{self._name} {self.type}"
        sql += "".join(f" {c}" for c in self.constraints)
        return sql

    @property
    def full_name(self) -> str:
        """Fully qualified name for the column."""
        if self.table:
            return f"{self.table}.{self._name}"
        else:
            return self.name

    def bind_table(self, table: Table) -> Column:
        """Bind the given table to this column."""
        self.table = table
        return self

    def as_(self, alias: str) -> str:
        """Sets an alias name to represent this column and returns it's definition."""
        definition = f"{self.full_name} AS {alias}"
        self.alias = alias
        return definition

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
        return aggregates.Avg(self).as_(f"{self.name}_avg")

    @property
    def bit_and(self) -> aggregates.BitAnd:
        """Bitwise AND of all non-null values in this column."""
        return aggregates.BitAnd(self).as_(f"{self.name}_bit_and")

    @property
    def bit_or(self) -> aggregates.BitOr:
        """Bitwise OR of all non-null values in this column."""
        return aggregates.BitOr(self).as_(f"{self.name}_bit_or")

    @property
    def bool_and(self) -> aggregates.BoolAnd:
        """Returns True if ALL non-null values in this column are True."""
        return aggregates.BoolAnd(self).as_(f"{self.name}_bool_and")

    @property
    def bool_or(self) -> aggregates.BoolOr:
        """Returns True if ANY non-null values in this column are True."""
        return aggregates.BoolOr(self).as_(f"{self.name}_bool_or")

    @property
    def count(self) -> aggregates.Count:
        """Counts of all rows."""
        return aggregates.Count(self).as_(f"{self.name}_count")

    @property
    def max(self) -> aggregates.Max:
        """Maximum of all non-null values in this column."""
        return aggregates.Max(self).as_(f"{self.name}_max")

    @property
    def min(self) -> aggregates.Min:
        """Minimum of all non-null values in this column."""
        return aggregates.Min(self).as_(f"{self.name}_min")

    @property
    def sum(self) -> aggregates.Sum:
        """Sum of all non-null values in this column."""
        return aggregates.Sum(self).as_(f"{self.name}_sum")

    # endregion

    # region: query modifiers

    @property
    def asc(self) -> Column:
        self._sort_direction = "ASC"
        return self

    @property
    def desc(self) -> Column:
        self._sort_direction = "DESC"
        return self
