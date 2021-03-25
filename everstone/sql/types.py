from __future__ import annotations

import abc
import datetime
import decimal
import typing as t
import zoneinfo

__all__ = (
    "Integer", "SmallInteger", "BigInteger", "Serial", "SmallSerial", "BigSerial", "Numeric", "Decimal", "Real",
    "DoublePrecision", "Money", "Text", "ByteA", "Timestamp", "TimestampTZ", "Date", "Time", "Interval", "Boolean",
    "JSON", "JSONB", "Array", "SQLType",
)


# region: Bases

class SpecialValue(abc.ABC):
    """Represents a special value specific to an SQL Type."""

    def __init__(self, python_value: t.Any, sql_value: str):
        self._py_value = python_value
        self.sql = sql_value

    @property
    def py(self) -> t.Any:
        """Python representation of the special value."""
        if isinstance(self._py_value, t.Callable):
            return self._py_value()
        else:
            return self._py_value

    def __repr__(self):
        return f"SpecialValue({self.py}, '{self.sql})'"

    def __str__(self):
        return self.sql

    def __eq__(self, other: t.Any):
        if not isinstance(other, SpecialValue):
            return False
        return self.sql == other.sql and self._py_value == other._py_value


class SQLTypeMeta(abc.ABCMeta):
    """Metaclass defining the behaviour of non-initialised SQLType classes."""

    __types__ = dict()
    py: t.Any
    sql: str

    def __init__(cls, *_args, **_kwargs):
        super().__init__(cls)
        if cls.__name__ == "SQLType":
            return
        SQLTypeMeta.__types__[cls.py] = cls

    def __repr__(self):
        classname = self.__name__
        return f'<{classname} python={self.py.__name__} sql="{self.sql}">'

    def __str__(self):
        return self.sql

    def __eq__(self, other: t.Any):
        if isinstance(other, SQLTypeMeta) or isinstance(type(other), SQLTypeMeta):
            return self.sql == other.sql
        return False


class SQLType(metaclass=SQLTypeMeta):
    """Base class representing an SQL datatype."""

    py: t.Any
    sql: str

    def __init__(self):
        pass

    def __repr__(self):
        classname = self.__class__.__name__
        return f'<{classname} python={self.py.__name__} sql="{self.sql}">'

    def __str__(self):
        return self.sql

    def __eq__(self, other: t.Any):
        if isinstance(other, SQLTypeMeta) or isinstance(type(other), SQLTypeMeta):
            return self.sql == other.sql
        return False


# endregion


# region: Numeric Types

class Integer(SQLType):
    """
    Whole number from -32768 to +32767.

    Uses 4 bytes of storage.
    """

    py = int
    sql = "INTEGER"


class SmallInteger(Integer):
    """
    Whole number from -2147483648 to +2147483647.

    Uses 2 bytes of storage.
    """

    sql = "SMALLINT"


class BigInteger(Integer):
    """
    Whole number from -9223372036854775808 to +9223372036854775807.

    Uses 8 bytes of storage.
    """

    sql = "BIGINT"


class Serial(Integer):
    """
    Auto-incrementing number from 1 to 2147483647.

    Uses 4 bytes of storage.
    """

    sql = "SERIAL"


class SmallSerial(Serial):
    """
    Auto-incrementing number from 1 to 32767.

    Uses 2 bytes of storage.
    """

    sql = "SMALLSERIAL"


class BigSerial(Serial):
    """
    Auto-incrementing number from 1 to 9223372036854775807.

    Uses 8 bytes of storage.
    """

    sql = "BIGSERIAL"


class Numeric(SQLType):
    """
    Precise decimal number with configurable precision and scale.

    Uses 3 to 8 bytes overhead and 2 bytes for every 4 decimal digits.
    """

    py = decimal.Decimal
    sql = "NUMERIC"

    # special values
    not_a_number = SpecialValue(decimal.Decimal("NaN"), "'NaN'")

    def __init__(self, precision: int, scale: int = 0):  # noqa
        self.precision = precision
        self.scale = scale
        self.sql = f"NUMERIC({precision}, {scale})"


class Decimal(Numeric):
    """
    Precise decimal number with configurable precision and scale.

    Uses 3 to 8 bytes storage overhead and 2 bytes for every 4 decimal digits.
    """

    sql = "DECIMAL"


class Real(SQLType):
    """
    Inexact floating-point number with a range of 1E-37 to 1E+37.

    Uses 4 bytes of storage.
    """

    py = float
    sql = "REAL"

    # special values
    not_a_number = SpecialValue(float("NaN"), "'NaN'")
    infinity = SpecialValue(float("inf"), "'Infinity'")
    negative_infinity = SpecialValue(float("-inf"), "'-Infinity'")


class DoublePrecision(Real):
    """
    Inexact floating-point number with a range of 1E-307 to 1E+308.

    Uses 8 bytes of storage.
    """

    sql = "DOUBLE PRECISION"


class Money(SQLType):
    """
    Currency amount with a fixed precision ranging from -92233720368547758.08 to +92233720368547758.07.

    Uses 8 bytes of storage.
    """

    py = str
    sql = "MONEY"


# endregion


# region: String Types

class Text(SQLType):
    """
    Variable unlimited string.

    Uses 1 byte of storage overhead for strings under 126 bytes in length, or 4 bytes if over that length.
    """

    py = str
    sql = "TEXT"


class ByteA(SQLType):
    """
    Variable unlimited binary string.

    Uses 1 byte of storage overhead for strings under 126 bytes in length, or 4 bytes if over that length.
    """

    py = bytes
    sql = "BYTEA"


# endregion


# region: DateTime Types

class Timestamp(SQLType):
    """
    Timezone naive datetime.

    Uses 8 bytes of storage.
    """

    py = datetime.datetime
    sql = "TIMESTAMP"

    # special values
    epoch = SpecialValue(datetime.datetime.utcfromtimestamp(0), "'Epoch'")
    infinity = SpecialValue(datetime.datetime.max, "'Infinity'")
    negative_infinity = SpecialValue(datetime.datetime.min, "'-Infinity'")
    now = SpecialValue(datetime.datetime.now, "Now")
    today = SpecialValue(datetime.datetime.today, "Today")
    tomorrow = SpecialValue(lambda: datetime.datetime.today() + datetime.timedelta(days=1), "Tomorrow")
    yesterday = SpecialValue(lambda: datetime.datetime.today() + datetime.timedelta(days=-1), "Yesterday")

    def __init__(self, precision: int):  # noqa
        self.precision = precision
        self.sql = f"TIMESTAMP({precision})"


class TimestampTZ(Timestamp):
    """
    Timezone aware datetime.

    Uses 8 bytes of storage.
    """

    sql = "TIMESTAMP WITH TIME ZONE"

    def __init__(self, precision: int):  # noqa
        self.precision = precision
        self.sql = f"TIMESTAMP({precision}) WITH TIME ZONE"


class Date(SQLType):
    """
    Date from 4713BC to 5874897AD.

    Uses 4 bytes of storage.
    """

    py = datetime.date
    sql = "DATE"

    # special values
    epoch = SpecialValue(datetime.datetime.utcfromtimestamp(0).date(), "'Epoch'")
    infinity = SpecialValue(datetime.datetime.max.date(), "'Infinity'")
    negative_infinity = SpecialValue(datetime.datetime.min.date(), "'-Infinity'")
    now = SpecialValue(datetime.date.today, "Now")
    today = SpecialValue(datetime.date.today, "Today")
    tomorrow = SpecialValue(lambda: datetime.date.today() + datetime.timedelta(days=1), "Tomorrow")
    yesterday = SpecialValue(lambda: datetime.date.today() + datetime.timedelta(days=-1), "Yesterday")


class Time(SQLType):
    """
    Timezone naive time of day.

    Uses 8 bytes of storage.
    """

    py = datetime.time
    sql = "TIME"

    # special values
    now = SpecialValue(lambda: datetime.datetime.now().time(), "Now")
    allballs = SpecialValue(datetime.time(0, 0, 0, 0, zoneinfo.ZoneInfo("UTC")), "Allballs")

    def __init__(self, precision: int):  # noqa
        self.precision = precision
        self.sql = f"TIME({precision})"


class Interval(SQLType):
    """
    Time interval.

    Uses 16 bytes of storage.
    """

    py = datetime.timedelta
    sql = "INTERVAL"

    def __init__(self, precision: int):  # noqa
        self.precision = precision


# endregion


# region: Boolean Types

class Boolean(SQLType):
    """
    True or False value.

    Uses 1 byte of storage.
    """

    py = bool
    sql = "BOOLEAN"


# endregion


# region: Collection Types

class JSON(SQLType):
    """JSON data objects."""

    py = dict
    sql = "JSON"


class JSONB(SQLType):
    """JSONB data objects."""

    py = dict
    sql = "JSONB"


class Array(SQLType):
    """Variable length array containing any supported type."""

    py = list

    def __init__(self, element_type: SQLType, size: int = ''):  # noqa
        self.element_type = element_type
        self.element_size = size
        self.sql = f"{element_type}[{size}]"

# endregion
