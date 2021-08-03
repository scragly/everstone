"""Testing of SQL Column functionality."""
import pytest

import everstone
from everstone.exceptions import SchemaError
from everstone.sql import column, constraints, types


@pytest.fixture
def test_col():
    return column.Column("example_column", types.Text, constraints.Unique)


def test_column_unbound_names():
    col = column.Column("testing_a", types.Text)
    assert col.name == "testing_a"
    assert col.full_name == "testing_a"
    assert str(col) == "testing_a"
    assert col == "testing_a"
    assert repr(col) == "<Column testing_a TEXT>"
    assert col.as_("alias_a") == "testing_a AS alias_a"
    assert col.full_name == "alias_a"


def test_column_bound_names():
    col = everstone.db.Table("target_table").Column("testing_b", types.Text)
    assert col.name == "testing_b"
    assert col.full_name == "public.target_table.testing_b"
    assert str(col) == "public.target_table.testing_b"
    assert col == "public.target_table.testing_b"
    assert repr(col) == "<Column public.target_table.testing_b TEXT>"


def test_column_definition(test_col):
    assert test_col.definition == "example_column TEXT UNIQUE"
    assert test_col.constraints == {constraints.Unique, }
    assert (test_col == "value") == "example_column = 'value'"


def test_column_modifiers(test_col):
    assert test_col.grouped._grouped is True
    assert test_col.asc.sort_direction == "ASC"
    assert test_col.desc.sort_direction == "DESC"
    test_col.reset_modifiers()
    assert test_col._grouped is False
    assert test_col.sort_direction is None


def test_column_defaults():
    with pytest.raises(SchemaError, match="No default is set*"):
        _ = column.Column("no_default", types.Text).default
    assert column.Column("has_default", types.Text, default="something").default == "something"


def test_column_aggregates(test_col):
    assert test_col.avg == "avg(example_column) AS example_column_avg"
    assert test_col.bit_and == "bit_and(example_column) AS example_column_bit_and"
    assert test_col.bit_or == "bit_or(example_column) AS example_column_bit_or"
    assert test_col.bool_and == "bool_and(example_column) AS example_column_bool_and"
    assert test_col.bool_or == "bool_or(example_column) AS example_column_bool_or"
    assert test_col.count == "count(example_column) AS example_column_count"
    assert test_col.max == "max(example_column) AS example_column_max"
    assert test_col.min == "min(example_column) AS example_column_min"
    assert test_col.sum == "sum(example_column) AS example_column_sum"
