"""Testing of Database functionality."""

import pytest

import everstone
from everstone.database import Database
from everstone.exceptions import DBError

everstone.db.disable_execution()


def test_db():
    db = Database("testing_db_a")
    assert db is everstone.db("testing_db_a")
    assert str(db) == "testing_db_a"
    assert repr(db) == "<Database 'testing_db_a'>"
    assert db.name == "testing_db_a"
    db = db.connect("testing_db_a", "user_a", "password_a", host="host_a", port=1234)
    assert db.url == "postgres://user_a:password_a@host_a:1234/testing_db_a"
    assert str(db) == "postgres://user_a:password_a@host_a:1234/testing_db_a"
    assert db.name == "testing_db_a"
    assert db.user == "user_a"
    assert db is everstone.db["testing_db_a"]
    assert everstone.db is not db
    assert hash(everstone.db) != hash(db)
    assert everstone.db != db
    assert db != 1
    assert repr(db) == "<Database 'testing_db_a' user='user_a'>"
    db.disable_execution()
    assert repr(db) == "<Database 'testing_db_a' user='user_a' disabled>"
    del db["testing_db_a"]
    assert len(db.__instances__) == 1
    assert everstone.db.connect("testing_db_b", "user_b", "password_b") is everstone.db["testing_db_b"]
    assert everstone.db is everstone.db["testing_db_b"]
    assert everstone.db["testing_db_b"].url == "postgres://user_b:password_b@localhost:5432/testing_db_b"
    assert len(db.__instances__) == 2
    everstone.db.name = "__default__"


def test_db_connect():
    default = everstone.db
    assert len(everstone.db.__instances__) == 2
    db = everstone.db.connect("testing_db_c", "user_c", "password_c")
    assert len(db.__instances__) == 3
    assert db is everstone.db["testing_db_c"]
    assert everstone.db is not db
    Database.__instances__.clear()
    Database.__instances__["__default__"] = default
    assert len(Database.__instances__) == 1


def test_db_default():
    assert everstone.db.get_default() is everstone.db


@pytest.mark.asyncio
async def test_db_pool():
    db = Database("test_db_d")
    assert db.url is None
    with pytest.raises(DBError):
        await db.create_pool()
    db.connect("__default__", "a", "b")
    assert everstone.db.url == "postgres://a:b@localhost:5432/__default__"
    with pytest.raises(OSError):
        await everstone.db.create_pool()
    with pytest.raises(AttributeError):
        everstone.db.pool = True
        await everstone.db.create_pool()
    default = everstone.db
    default.name = "__default__"
    Database.__instances__.clear()
    Database.__instances__["__default__"] = default
    default.enable_execution()
    default.disable_execution()


@pytest.mark.asyncio
async def test_db_prepare():
    with everstone.db.stmt_tracking():
        everstone.db.Schema("test_schema_a")
        await everstone.db.prepare()
        stmts = everstone.db._tracking.get()
    assert stmts == [
        ("CREATE SCHEMA IF NOT EXISTS test_schema_a;", ())
    ]
