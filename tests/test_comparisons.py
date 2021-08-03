"""Testing of Comparable Base SQL functionality."""
from everstone.sql import comparisons


class ComparableTesting(comparisons.Comparable):
    def __init__(self, value):
        self.value = self._sql_value(value)

    def __str__(self):
        return self.value


def test_comparable_values():
    assert str(ComparableTesting(None)) == "NULL"
    assert str(ComparableTesting(True)) == "TRUE"
    assert str(ComparableTesting(False)) == "FALSE"
    assert str(ComparableTesting(1)) == '1'
    assert str(ComparableTesting("testing_value")) == "'testing_value'"


def test_comparable_operators():
    hundred = ComparableTesting(100)
    assert (hundred < 500) == "100 < 500"
    assert (hundred <= 500) == "100 <= 500"
    assert (hundred == 500) == "100 = 500"
    assert (hundred != 500) == "100 <> 500"
    assert (hundred >= 500) == "100 >= 500"
    assert (hundred > 500) == "100 > 500"
    assert (hundred.between(0, 500)) == "100 BETWEEN 0 AND 500"
    assert (hundred.not_between(0, 500)) == "100 NOT BETWEEN 0 AND 500"
    example = ComparableTesting("example_text")
    assert (example.like("something")) == "'example_text' LIKE 'something'"
    assert (example.not_like("something")) == "'example_text' NOT LIKE 'something'"
    assert (example.ilike("something")) == "'example_text' ILIKE 'something'"
    assert (example.not_ilike("something")) == "'example_text' NOT ILIKE 'something'"
    assert (example.is_("something")) == "'example_text' IS 'something'"
    assert (example.is_not("something")) == "'example_text' IS NOT 'something'"
    assert (example.in_("something")) == "'example_text' IN 'something'"
