from __future__ import annotations

import abc
import typing as t

from .column import Column

if t.TYPE_CHECKING:
    from .table import Table


class ConstraintMeta(abc.ABCMeta):
    """Metaclass to define behaviour of non-initialised constraint classes."""

    sql: str

    def __repr__(self):
        return f'<{self.__name__} sql="{self.sql}">'

    def __str__(self):
        return self.sql

    def __eq__(self, other: t.Any):
        if isinstance(other, ConstraintMeta) or isinstance(type(other), ConstraintMeta):
            return self.sql == other.sql
        return False

    def named(cls, name: str) -> NamedConstraint:
        """Returns this constraint as a named constraint."""
        return NamedConstraint(cls, name)

    def columns(cls, *columns: Column) -> CompositeConstraint:
        """Returns this constraint as a composite constraint, using multiple columns."""
        return CompositeConstraint(cls, *columns)


class Constraint(metaclass=ConstraintMeta):
    """Base class representing an SQL constraint."""

    sql: str

    def __init__(self):
        self.named = self._named
        self.columns = self._columns

    def __repr__(self):
        return f'<{self.__class__.__name__} sql="{self.sql}">'

    def __str__(self):
        return self.sql

    def __eq__(self, other: t.Any):
        if isinstance(other, ConstraintMeta) or isinstance(type(other), ConstraintMeta):
            return self.sql == other.sql
        return False

    def _named(self, name: str) -> NamedConstraint:
        """Instance-specific implementation of Constraint.named."""
        return NamedConstraint(self, name)

    def _columns(self, *columns: Column) -> CompositeConstraint:
        """Instance-specific implementation of Constraint.columns."""
        return CompositeConstraint(self, *columns)


class NamedConstraint(Constraint):
    """Composite class representing a named SQL constraint."""

    def __init__(self, constraint: t.Union[Constraint, ConstraintMeta], name: str):
        self.columns = self._columns
        self.constraint = constraint
        self.name = name
        self.sql = f"CONSTRAINT {self.name} {self.constraint}"


class CompositeConstraint(Constraint):
    """Composite class representing an SQL constraint that uses more than one column."""

    def __init__(self, constraint: t.Union[Constraint, ConstraintMeta], *columns: t.Union[Column, str]):
        self.constraint = constraint
        self.columns = columns
        cols = ", ".join(c.name if isinstance(c, Column) else c for c in columns)
        self.sql = f"{constraint.sql} ({cols})"


class Check(Constraint):
    """Represents a CHECK SQL constraint."""

    sql: str

    def __init__(self, expression: str, *, name: t.Optional[str] = None):
        super().__init__()
        self.name = name
        self.expression = expression
        if name:
            self.sql = f"CONSTRAINT {self.name} CHECK ({expression})"
        else:
            self.sql = f"CHECK ({expression})"


class NotNull(Constraint):
    """Represents a NOT NULL SQL constraint."""

    sql = "NOT NULL"


class Unique(Constraint):
    """Represents a UNIQUE SQL constraint."""

    sql = "UNIQUE"


class PrimaryKey(Constraint):
    """Represents a PRIMARY KEY SQL constraint."""

    sql = "PRIMARY KEY"


class ForeignKey(Constraint):
    """Represents a foreign key SQL constraint using REFERENCES."""

    sql: str

    def __init__(self, table: t.Union[Table, str], column: t.Union[Column, str]):
        self.table = table
        self.column = column.name if isinstance(column, Column) else column
        self.sql = f"REFERENCES {self.table} ({self.column})"
