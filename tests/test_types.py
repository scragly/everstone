"""Testing of SQL Types functionality."""
import datetime
import decimal

import pytest

import everstone
from everstone.sql import types

everstone.db.disable_execution()


def test_type():
    t = types.Integer
    assert t.py == int
    assert t().py == int
    assert t.sql == "INTEGER"
    assert t().sql == "INTEGER"
    assert repr(t) == "<Integer python='int' sql='INTEGER'>"
    assert repr(t()) == "<Integer python='int' sql='INTEGER'>"
    assert str(t) == "INTEGER"
    assert str(t()) == "INTEGER"
    assert t == t()
    assert t != "INTEGER"
    assert t() == t
    assert t() != "INTEGER"
    assert hash(t) == hash("<Integer python='int' sql='INTEGER'>")
    assert hash(t()) == hash("<Integer python='int' sql='INTEGER'>")


def test_type_numeric():
    t = types.Numeric
    assert t.py == decimal.Decimal
    assert t.sql == "NUMERIC"
    t = t(2)
    assert t != types.Numeric
    assert t.py == decimal.Decimal
    assert t.sql == "NUMERIC(2, 0)"
    assert types.Numeric(2, 2).sql == "NUMERIC(2, 2)"


def test_type_timestamp():
    t = types.Timestamp
    assert t.py == datetime.datetime
    assert t.sql == "TIMESTAMP"
    assert t(2).sql == "TIMESTAMP(2)"
    assert t != t(2)


def test_type_timestamptz():
    t = types.TimestampTZ
    assert t.py == datetime.datetime
    assert t.sql == "TIMESTAMP WITH TIME ZONE"
    assert t(2).sql == "TIMESTAMP(2) WITH TIME ZONE"
    assert t != t(2)


def test_type_time():
    t = types.Time
    assert t.py == datetime.time
    assert t.sql == "TIME"
    assert t(2).sql == "TIME(2)"
    assert t != t(2)


def test_type_array():
    t = types.Array
    assert t.py == list
    with pytest.raises(AttributeError):
        _ = t.sql
    t = types.Array(types.Integer, 2)
    assert t.sql == "INTEGER[2]"
    t = types.Array(types.Integer)
    assert t.sql == "INTEGER[]"


def test_type_special_values():
    assert types.Date.tomorrow.sql == "Tomorrow"
    assert types.Date.tomorrow.py == datetime.date.today() + datetime.timedelta(days=1)
    nan = types.Numeric.not_a_number
    assert nan.sql == "'NaN'"
    assert decimal.Decimal.is_nan(nan.py)
    assert repr(nan) == "SpecialValue(NaN, \"'NaN'\")"
    assert str(nan) == "'NaN'"
    assert types.Date.tomorrow == types.Date.tomorrow
    assert types.Date.tomorrow != 1
    assert types.Timestamp.tomorrow.py != types.Timestamp.yesterday.py
    assert types.Date.yesterday.py != types.Time.now.py
