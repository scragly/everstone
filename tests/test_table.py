"""Testing of SQL Table functionality."""

import pytest

import everstone
from everstone.exceptions import SchemaError
from everstone.sql import constraints, types

everstone.db.disable_execution()


def test_table():
    t = everstone.db.Table("test_table_a")
    assert t.name == "test_table_a"
    assert t.schema == everstone.db.public_schema
    assert t.full_name == "public.test_table_a"
    assert str(t) == "public.test_table_a"
    assert repr(t) == "<Table public.test_table_a>"
    t.Column("col_a", types.Text)
    assert repr(t) == "<Table public.test_table_a (col_a)>"
    assert t == everstone.db.Table("test_table_a")
    assert t != "test_table_a"


@pytest.mark.asyncio
async def test_table_create():
    db = everstone.db
    t = db.Table("test_table_a")
    with pytest.raises(SchemaError):
        await t.create()
    t.Column("col_a", types.Text)
    t.add_columns(everstone.Column("col_b", types.Integer))
    assert len(t.columns) == 2
    assert t.columns["col_a"].name == "col_a"
    assert t.columns.col_a.name == "col_a"
    assert t.columns.col_b.type == db.type.Integer
    with pytest.raises(AttributeError):
        _ = t.columns.col_nonexisting
    assert await t.create() == "CREATE TABLE test_table_a (col_a TEXT, col_b INTEGER);"
    with db.stmt_tracking():
        await t.prepare()
        stmts = everstone.db._tracking.get()
    assert stmts == [
        ("CREATE TABLE IF NOT EXISTS test_table_a (col_a TEXT, col_b INTEGER);", ())
    ]


def test_table_count():
    assert everstone.db.Table("test_table_a").count.sql == "count(public.test_table_a.*)"


@pytest.mark.asyncio
async def test_table_constraints():
    t = everstone.db.Table("test_table_a")
    a = t.Column("col_a", types.Text)
    b = t.Column("col_b", types.Integer)
    t.add_constraints(constraints.CompositeConstraint(constraints.PrimaryKey, a, b))
    assert await t.create() == "CREATE TABLE test_table_a (col_a TEXT, col_b INTEGER, PRIMARY KEY (col_a, col_b));"


@pytest.mark.asyncio
async def test_table_drop():
    t = everstone.db.Table("test_table_a")
    assert await t.drop() == "DROP TABLE test_table_a;"
    assert await t.drop(if_exists=True, cascade=True) == "DROP TABLE IF EXISTS test_table_a CASCADE;"


def test_table_select():
    t = everstone.db.Table("test_table_a")
    a = t.Column("col_a", types.Text)
    s = t.select(a)
    assert s.db is everstone.db
    assert len(s._rows) == 1
