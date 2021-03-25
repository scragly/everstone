from __future__ import annotations

import json
import logging
import typing as t

import asyncpg
import sqlparse

from .bases import LimitInstances
from .sql import types
from .sql.schema import Schema
from .sql.table import Table

log = logging.getLogger(__name__)


class Database(LimitInstances):
    """Represents a database."""

    def __init__(self, name: str):
        self.name = name
        self.user: t.Optional[str] = None
        self.url: t.Optional[str] = None

        self.pool: t.Optional[asyncpg.Pool] = None

        self.type = types
        self.schemas: t.Set[Schema] = set()

        self._mock = False
        self._prepared = False

    @classmethod
    def connect(cls, name: str, user: str, password: str, *, host: str = "localhost", port: int = 5432) -> Database:
        """Establish the connection URL and name for the database, returning the instance representing it."""
        if len(cls.__instances__) == 1:
            db = cls.__instances__["__default__"]
            cls.__instances__[name] = db
            db.name = name
            db.user = user
            db.url = f"postgres://{user}:{password}@{host}:{port}/{name}"
            # noinspection PyTypeChecker
            return db

        return Database(name)

    def __call__(self, name: str) -> Database:
        """Return the instance representing the given database name."""
        return Database(name)

    def __str__(self):
        """Return the URL representation of the given database instance, if set."""
        return self.url or self.name

    def __repr__(self):
        if self.user:
            return f"<Database name='{self.name}' user='{self.user}'>"
        else:
            return f"<Database '{self.name}'>"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: t.Any):
        if isinstance(other, Database):
            return str(self) == str(self)
        return False

    async def create_pool(self):
        """Create the asyncpg connection pool for this database connection to use."""
        if self.pool:
            self.pool.close()
        self.pool = await asyncpg.create_pool(self.url, init=self._enable_json)

    @staticmethod
    async def _enable_json(conn: asyncpg.Connection):
        await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
        await conn.set_type_codec("json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")

    async def prepare(self):
        """Prepare all child objects for this database."""
        for schema in self.schemas:
            await schema.prepare()
        self._prepared = True

    def disable_execution(self):
        """Don't execute SQL statements, divert them to console output instead."""
        self._mock = True

    def enable_execution(self):
        """Restore normal SQL execution status instead of diverting statements to console output."""
        self._mock = False

    async def close(self):
        """Close the asyncpg connection pool for this database."""
        if self.pool:
            await self.pool.close()

    async def execute(self, sql: str, *args, timeout: t.Optional[float] = None) -> str:
        """Execute an SQL statement."""
        if self._mock:
            pretty_sql = sqlparse.parse(sql)
            print(pretty_sql, *args)
            return pretty_sql
        return await self.pool.execute(sql, *args, timeout=timeout)

    def Schema(self, name: str) -> Schema:
        """Return a bound Schema for this database."""
        return Schema(name, self)

    def Table(self, name: str) -> Table:
        """Return a bound Table for the public schema on this database."""
        return Table(name, self)
