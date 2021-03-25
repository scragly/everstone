import abc
import typing as t


class Comparable(abc.ABC):
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

    def __lt__(self, value: t.Any) -> str:
        """Evaluate if less than a value."""
        value = self._sql_value(value)
        return f"{self} < {value}"

    def __le__(self, value: t.Any) -> str:
        """Evaluate if less than or equal to a value."""
        value = self._sql_value(value)
        return f"{self} <= {value}"

    def __eq__(self, value: t.Any) -> str:
        """Evaluate if equal to a value."""
        value = self._sql_value(value)
        return f"{self} = {value}"

    def __ne__(self, value: t.Any) -> str:
        """Evaluate if not equal to a value."""
        value = self._sql_value(value)
        return f"{self} <> {value}"

    def __gt__(self, value: t.Any) -> str:
        """Evaluate if greater than a value."""
        value = self._sql_value(value)
        return f"{self} > {value}"

    def __ge__(self, value: t.Any) -> str:
        """Evaluate if greater than or equal to a value."""
        value = self._sql_value(value)
        return f"{self} >= {value}"

    def like(self, value: t.Any) -> str:
        """Evaluate if like a value."""
        value = self._sql_value(value)
        return f"{self} LIKE {value}"

    def not_like(self, value: t.Any) -> str:
        """Evaluate if not like a value."""
        value = self._sql_value(value)
        return f"{self} NOT LIKE {value}"

    def ilike(self, value: t.Any) -> str:
        """Evaluate if like a value, ignoring case."""
        value = self._sql_value(value)
        return f"{self} ILIKE {value}"

    def not_ilike(self, value: t.Any) -> str:
        """Evaluate if not like a value, ignoring case."""
        value = self._sql_value(value)
        return f"{self} NOT ILIKE {value}"

    def between(self, minvalue: t.Any, maxvalue: t.Any) -> str:
        """Evaluate if between two values."""
        minvalue = self._sql_value(minvalue)
        maxvalue = self._sql_value(maxvalue)
        return f"{self} BETWEEN {minvalue} AND {maxvalue}"

    def not_between(self, minvalue: t.Any, maxvalue: t.Any) -> str:
        """Evaluate if not between two values."""
        minvalue = self._sql_value(minvalue)
        maxvalue = self._sql_value(maxvalue)
        return f"{self} NOT BETWEEN {minvalue} AND {maxvalue}"

    def is_(self, value: t.Any) -> str:
        """Evaluate if is a value."""
        value = self._sql_value(value)
        return f"{self} IS {value}"

    def is_not(self, value: t.Any) -> str:
        """Evaluate if is not a value."""
        value = self._sql_value(value)
        return f"{self} IS NOT {value}"

    def in_(self, value: t.Any) -> str:
        """Evaluate if in a value."""
        value = self._sql_value(value)
        return f"{self} IN {value}"
