"""Testing of SQL Aggregate functionality."""
import pytest

import everstone
from everstone.sql import aggregates


@pytest.fixture
def str_column_sample():
    return "string_column_a"


@pytest.fixture
def obj_column_sample():
    return everstone.Column("obj_column_b", everstone.types.Text)


@pytest.fixture
def table_sample():
    return everstone.db.Table("example_table")


def test_agg_col_str(str_column_sample):
    """Test aggregate whe using a string as column arg."""
    aggregates.Aggregate.name = "test_agg_col_str"
    agg = aggregates.Aggregate(str_column_sample)
    assert agg.name == "test_agg_col_str"
    assert agg.sql == "test_agg_col_str(string_column_a)"
    assert str(agg) == "test_agg_col_str(string_column_a)"
    assert repr(agg) == "<Aggregate 'test_agg_col_str(string_column_a)'>"
    assert agg.as_("test_alias") == "test_agg_col_str(string_column_a) AS test_alias"
    assert str(agg) == "test_alias"
    assert agg.distinct.sql == "test_agg_col_str(DISTINCT string_column_a)"
    assert (agg == "value") == "test_alias = 'value'"


def test_agg_col_obj(obj_column_sample):
    """Test aggregate whe using a Column object arg."""
    aggregates.Aggregate.name = "test_agg_col_obj"
    agg = aggregates.Aggregate(obj_column_sample)
    assert agg.name == "test_agg_col_obj"
    assert agg.sql == "test_agg_col_obj(obj_column_b)"
    assert str(agg) == "test_agg_col_obj(obj_column_b)"
    assert repr(agg) == "<Aggregate 'test_agg_col_obj(obj_column_b)'>"
    assert agg.as_("test_alias") == "test_agg_col_obj(obj_column_b) AS test_alias"
    assert str(agg) == "test_alias"
    assert agg.distinct.sql == "test_agg_col_obj(DISTINCT obj_column_b)"
    assert (agg == "value") == "test_alias = 'value'"


def test_avg(str_column_sample, obj_column_sample):
    """Test Avg aggregate."""
    assert aggregates.Avg(str_column_sample).sql == "avg(string_column_a)"


def test_bit_and(str_column_sample, obj_column_sample):
    """Test BitAnd aggregate."""
    assert aggregates.BitAnd(str_column_sample).sql == "bit_and(string_column_a)"


def test_bit_or(str_column_sample, obj_column_sample):
    """Test BitOr aggregate."""
    assert aggregates.BitOr(str_column_sample).sql == "bit_or(string_column_a)"


def test_bool_and(str_column_sample):
    """Test BoolAnd aggregate."""
    assert aggregates.BoolAnd(str_column_sample).sql == "bool_and(string_column_a)"


def test_bool_or(str_column_sample):
    """Test BoolOr aggregate."""
    assert aggregates.BoolOr(str_column_sample).sql == "bool_or(string_column_a)"


def test_count(str_column_sample, table_sample):
    """Test Count aggregate."""
    assert aggregates.Count(str_column_sample).sql == "count(string_column_a)"
    assert aggregates.Count().sql == "count(*)"
    assert aggregates.Count.all() == "count(*)"
    assert aggregates.Count(table_sample).sql == "count(public.example_table.*)"


def test_max(str_column_sample):
    """Test Max aggregate."""
    assert aggregates.Max(str_column_sample).sql == "max(string_column_a)"


def test_min(str_column_sample):
    """Test Min aggregate."""
    assert aggregates.Min(str_column_sample).sql == "min(string_column_a)"


def test_sum(str_column_sample):
    """Test Sum aggregate."""
    assert aggregates.Sum(str_column_sample).sql == "sum(string_column_a)"
