"""Testing of Select statement functionality."""

import pytest

import everstone
from everstone.sql import constraints, types

everstone.db.disable_execution()


@pytest.fixture
def sample_table():
    t = everstone.db.Table("sample_table")
    t.Column("col_a", types.Text, constraints.PrimaryKey)
    t.Column("col_b", types.Integer)
    return t


def test_select(sample_table):
    s = sample_table.select
    assert s.sql == "SELECT NULL"
    s = sample_table.select(sample_table.columns.col_a)
    assert s.sql == "SELECT public.sample_table.col_a FROM public.sample_table;"
    assert str(s) == "SELECT public.sample_table.col_a FROM public.sample_table;"
    assert repr(s) == "<Select 'SELECT public.sample_table.col_a FROM public.sample_table;'>"
    assert s.columns == (sample_table.columns.col_a,)


@pytest.mark.asyncio
async def test_select_distinct(sample_table):
    s = sample_table.select(sample_table.columns.col_a)
    assert s.sql == "SELECT public.sample_table.col_a FROM public.sample_table;"
    assert await s.distinct == "SELECT DISTINCT public.sample_table.col_a FROM public.sample_table;"
    s = sample_table.select.distinct_on(sample_table.columns.col_a, sample_table.columns.col_b)
    assert await s == (
        "SELECT DISTINCT ON (public.sample_table.col_a, public.sample_table.col_b)"
        " public.sample_table.col_a, public.sample_table.col_b"
        " FROM public.sample_table;"
    )


@pytest.mark.asyncio
async def test_select_grouped(sample_table):
    col_a = sample_table.columns.col_a
    s = sample_table.select(col_a.count)
    s.group_by(col_a)
    assert s.groups == [col_a]
    assert await s == "SELECT count(public.sample_table.col_a) AS col_a_count GROUP BY public.sample_table.col_a;"
