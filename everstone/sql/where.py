from __future__ import annotations

import typing as t

from .comparisons import Condition


class Where:
    def __init__(self, query):
        self.query = query
        self._conditions: list[Condition] = []

    def add_condition(self, condition: Condition):
        self._conditions.append(condition)

    def clear(self):
        self._conditions.clear()

    def __call__(self, *conditions: t.Union[Condition, str]) -> Where:
        for c in conditions:
            if isinstance(c, str):
                c = Condition(c)
            self.add_condition(c)
        return self

    @property
    def sql(self):
        return " AND ".join(str(c) for c in self._conditions)
