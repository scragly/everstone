from __future__ import annotations

import abc
import typing as t


class Condition:
    def __init__(self, expression: t.Union[str, Condition]):
        self.expression = expression

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return f'<Condition "{self.expression}">'

    def __eq__(self, other):
        return str(self) == str(other)

    def __and__(self, other):
        return Condition(f"({self} AND {other})")

    def __or__(self, other):
        return Condition(f"({self} OR {other})")

    @classmethod
    def and_(cls, *conditions):  # pragma: no cover
        joined = " AND ".join(str(c) for c in conditions)
        return cls(f"({joined})")

    @classmethod
    def or_(cls, *conditions):  # pragma: no cover
        joined = " OR ".join(str(c) for c in conditions)
        return cls(f"({joined})")

    def and_(self, *conditions):
        joined = " AND ".join(str(c) for c in [self, *conditions])
        return Condition(f"({joined})")

    def or_(self, *conditions):
        joined = " OR ".join(str(c) for c in [self, *conditions])
        return Condition(f"({joined})")


class Comparable(metaclass=abc.ABCMeta):
    """Base class to define an SQL object as able to use SQL comparison operations."""

    @staticmethod
    def _sql_value(value: t.Any) -> str:
        """Adjusts a given value into an appropriate representation for SQL statements."""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return f"{value}"

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, value: t.Any) -> Condition:
        """Evaluate if less than a value."""
        value = self._sql_value(value)
        return Condition(f"{self} < {value}")

    def __le__(self, value: t.Any) -> Condition:
        """Evaluate if less than or equal to a value."""
        value = self._sql_value(value)
        return Condition(f"{self} <= {value}")

    def __eq__(self, value: t.Any) -> Condition:
        """Evaluate if equal to a value."""
        value = self._sql_value(value)
        return Condition(f"{self} = {value}")

    def __ne__(self, value: t.Any) -> Condition:
        """Evaluate if not equal to a value."""
        value = self._sql_value(value)
        return Condition(f"{self} <> {value}")

    def __gt__(self, value: t.Any) -> Condition:
        """Evaluate if greater than a value."""
        value = self._sql_value(value)
        return Condition(f"{self} > {value}")

    def __ge__(self, value: t.Any) -> Condition:
        """Evaluate if greater than or equal to a value."""
        value = self._sql_value(value)
        return Condition(f"{self} >= {value}")

    def like(self, value: t.Any) -> Condition:
        """Evaluate if like a value."""
        value = self._sql_value(value)
        return Condition(f"{self} LIKE {value}")

    def not_like(self, value: t.Any) -> Condition:
        """Evaluate if not like a value."""
        value = self._sql_value(value)
        return Condition(f"{self} NOT LIKE {value}")

    def ilike(self, value: t.Any) -> Condition:
        """Evaluate if like a value, ignoring case."""
        value = self._sql_value(value)
        return Condition(f"{self} ILIKE {value}")

    def not_ilike(self, value: t.Any) -> Condition:
        """Evaluate if not like a value, ignoring case."""
        value = self._sql_value(value)
        return Condition(f"{self} NOT ILIKE {value}")

    def between(self, minvalue: t.Any, maxvalue: t.Any) -> Condition:
        """Evaluate if between two values."""
        minvalue = self._sql_value(minvalue)
        maxvalue = self._sql_value(maxvalue)
        return Condition(f"{self} BETWEEN {minvalue} AND {maxvalue}")

    def not_between(self, minvalue: t.Any, maxvalue: t.Any) -> Condition:
        """Evaluate if not between two values."""
        minvalue = self._sql_value(minvalue)
        maxvalue = self._sql_value(maxvalue)
        return Condition(f"{self} NOT BETWEEN {minvalue} AND {maxvalue}")

    def is_(self, value: t.Any) -> Condition:
        """Evaluate if is a value."""
        value = self._sql_value(value)
        return Condition(f"{self} IS {value}")

    def is_not(self, value: t.Any) -> Condition:
        """Evaluate if is not a value."""
        value = self._sql_value(value)
        return Condition(f"{self} IS NOT {value}")

    def in_(self, value: t.Any) -> Condition:
        """Evaluate if in a value."""
        value = self._sql_value(value)
        return Condition(f"{self} IN {value}")
