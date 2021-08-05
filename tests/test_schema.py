"""Testing of SQL Schema functionality."""

import pytest

import everstone
from everstone.sql import constraints, types

everstone.db.disable_execution()


@pytest.fixture
def example_schema():
    return everstone.db.Schema("schema_a")


def test_schema(example_schema):
    assert example_schema.name == "schema_a"
    assert str(example_schema) == "schema_a"
    assert repr(example_schema) == "<Schema 'schema_a' on '__default__'>"
    assert id(everstone.db.Schema("schema_b")) != id(example_schema)
    assert id(everstone.db.Schema("schema_a")) == id(example_schema)


@pytest.mark.asyncio
async def test_schema_create(example_schema):
    assert example_schema.exists is None
    assert await example_schema.create() == "CREATE SCHEMA schema_a;"
    assert example_schema.exists is True
    assert await example_schema.create(if_exists=False) == "CREATE SCHEMA IF NOT EXISTS schema_a;"


@pytest.mark.asyncio
async def test_schema_drop(example_schema):
    assert example_schema.exists is None
    assert await example_schema.drop() == "DROP SCHEMA schema_a;"
    assert example_schema.exists is False
    assert await example_schema.drop(if_exists=True) == "DROP SCHEMA IF EXISTS schema_a;"
    assert await example_schema.drop(if_exists=True, cascade=True) == "DROP SCHEMA IF EXISTS schema_a CASCADE;"


@pytest.mark.asyncio
async def test_schema_rename(example_schema):
    assert example_schema.name == "schema_a"
    assert await example_schema.rename("schema_b") == ("ALTER SCHEMA schema_a RENAME TO $1;", "schema_b")
    assert example_schema.name == "schema_b"
    assert id(everstone.db.Schema("schema_a")) != id(example_schema)
    assert id(everstone.db.Schema("schema_b")) == id(example_schema)


@pytest.mark.asyncio
async def test_schema_prepare(example_schema):
    with everstone.db.stmt_tracking():
        example_schema.Table("table_a").Column("a_key_column", types.Text, constraints.PrimaryKey)
        example_schema.Table("table_b").Column("b_key_column", types.Integer, constraints.PrimaryKey)
        await example_schema.prepare()
        stmts = everstone.db._tracking.get()
    assert ("CREATE SCHEMA IF NOT EXISTS schema_a;", ()) in stmts
    assert ("CREATE TABLE IF NOT EXISTS table_b (b_key_column INTEGER PRIMARY KEY);", ()) in stmts
    assert ("CREATE TABLE IF NOT EXISTS table_a (a_key_column TEXT PRIMARY KEY);", ()) in stmts
    assert len(stmts) == 3
