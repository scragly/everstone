"""Testing of Where statement functionality."""

import pytest

import everstone
from everstone.sql import constraints, types

everstone.db.disable_execution()


@pytest.fixture
def example_table():
    t = everstone.db.Table("sample_table")
    t.Column("col_a", types.Text, constraints.PrimaryKey)
    t.Column("col_b", types.Integer)
    return t


def test_where(example_table):
    s = example_table.select("col_a")
    a = example_table.columns.col_a
    b = example_table.columns.col_b
    s.where(example_table.columns.col_a == example_table.columns.col_b)
    assert s.where.sql == "public.sample_table.col_a = public.sample_table.col_b"
    s.where.clear()
    assert s.where.sql == ""
    s.where(a=="john", b >= 100)
    assert s.where.sql == "public.sample_table.col_a = 'john' AND public.sample_table.col_b >= 100"
    s.where.clear()
    s.where(a.is_(True) | (a == 100) & b.ilike("dan"))
    assert s.where.sql == (
        "(public.sample_table.col_a IS TRUE"
        " OR (public.sample_table.col_a = 100"
        " AND public.sample_table.col_b ILIKE 'dan'))"
    )
    s.where.clear()
    s.where("string_example IS NOT NULL")
    assert s.where.sql == "string_example IS NOT NULL"
