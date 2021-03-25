from __future__ import annotations

import typing as t

from . import comparisons, table

if t.TYPE_CHECKING:
    from .column import Column


class Aggregate(comparisons.Comparable):
    """Represents an aggregate SQL function."""

    name: str

    def __init__(self, column: t.Optional[Column, str], alias: t.Optional[str] = None):
        self.column = column
        self.alias = alias

    @property
    def sql(self) -> str:
        """Generates the SQL statement representing the aggregate function."""
        if self.alias:
            return f"{self.name}({self.column}) AS {self.alias}"
        return f"{self.name}({self.column})"

    @property
    def distinct(self) -> Aggregate:
        """Sets column values to be DISTINCT when used in the aggregate function."""
        self.column = f"DISTINCT {self.column}"
        return self

    def as_(self, alias: str) -> Aggregate:
        """Sets an alias name to represent the result of the aggregate function."""
        self.alias = alias
        return self

    def __repr__(self) -> str:
        if self.alias:
            return f"<{self.__class__.__name__} alias={self.alias} column={self.column} sql='{self.sql}'>"
        return f"<{self.__class__.__name__} column={self.column} sql='{self.sql}'>"

    def __str__(self) -> str:
        return self.sql


class Avg(Aggregate):
    """Computes the average of all non-null input values."""

    name = "avg"


class BitAnd(Aggregate):
    """Computes the bitwise AND of all non-null input values."""

    name = "bit_and"


class BitOr(Aggregate):
    """Computes the bitwise OR of all non-null input values."""

    name = "bit_or"


class BoolAnd(Aggregate):
    """Returns TRUE if all non-null input values are TRUE, otherwise FALSE."""

    name = "bool_and"


class BoolOr(Aggregate):
    """Returns TRUE if any non-null input value is TRUE, otherwise FALSE."""

    name = "bool_or"


class Count(Aggregate):
    """Computes the number of input rows, counting only non-nulls if a column is specified."""

    name = "count"

    def __init__(self, value: t.Optional[Column, table.Table, str], alias: t.Optional[str] = None):
        if isinstance(value, table.Table):
            super().__init__(f"{value}.*" if value else "*", alias)
        else:
            super().__init__(f"{value}", alias)

    @classmethod
    def all(cls, alias: t.Optional = None) -> Count:
        """Computes the number of all input rows in a table."""
        return cls("*", alias)


class Max(Aggregate):
    """Computes the maximum of the non-null input values."""

    name = "max"


class Min(Aggregate):
    """Computes the minimum of the non-null input values."""

    name = "min"


class Sum(Aggregate):
    """Computes the sum of the non-null input values."""

    name = "sum"
