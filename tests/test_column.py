"""Testing of SQL Column functionality."""
import pytest

import everstone
from everstone.sql import column, types


@pytest.fixture
def test_col():
    return column.Column("example_column", types.Text)


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


def test_column_def(test_col):
    assert test_col.definition == "example_column TEXT"
    assert (test_col == "value") == "example_column = 'value'"


def test_column_sort(test_col):
    assert test_col.asc.sort_direction == "ASC"
    assert test_col.desc.sort_direction == "DESC"
