"""Testing of SQL Constraint functionality."""
import pytest

from everstone.sql import column, constraints, types


@pytest.fixture
def unique_instance():
    return constraints.Unique()


@pytest.fixture
def unique_class():
    return constraints.Unique


def test_constraint(unique_instance, unique_class):
    assert unique_instance.sql == "UNIQUE"
    assert str(unique_instance) == "UNIQUE"
    assert repr(unique_instance) == '<Unique sql="UNIQUE">'
    assert unique_instance == constraints.Unique()
    assert unique_instance != constraints.NotNull()
    assert unique_instance == unique_class
    assert unique_class.sql == "UNIQUE"
    assert str(unique_class) == "UNIQUE"
    assert repr(unique_class) == '<Unique sql="UNIQUE">'
    assert unique_class == constraints.Unique
    assert unique_class != constraints.NotNull()
    assert unique_class == unique_instance


def test_constraint_named(unique_instance, unique_class):
    assert unique_instance.named("unique_test").sql == "CONSTRAINT unique_test UNIQUE"
    assert unique_class.named("unique_test").sql == "CONSTRAINT unique_test UNIQUE"


def test_constraint_composite(unique_instance, unique_class):
    c = unique_instance.columns(column.Column("test_a", types.Text), column.Column("test_b", types.Text))
    assert c.sql == "UNIQUE (test_a, test_b)"
    c = unique_class.columns(column.Column("test_a", types.Text), column.Column("test_b", types.Text))
    assert c.sql == "UNIQUE (test_a, test_b)"
