from __future__ import annotations

import json
import logging
import typing as t

import asyncpg

from .bases import LimitInstances
from .exceptions import DBError
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
        else:
            db = Database(name)
        db.user = user
        db.url = f"postgres://{user}:{password}@{host}:{port}/{name}"
        return db

    @property
    def public_schema(self):
        return self.Schema("public")

    def __call__(self, name: str) -> Database:
        """Return the instance representing the given database name."""
        return Database(name)

    def __str__(self):
        """Return the URL representation of the given database instance, if set."""
        return self.url or self.name

    def __repr__(self):
        status = " disabled" if self._mock else ""
        if self.user:
            return f"<Database name='{self.name}' user='{self.user}'{status}>"
        else:
            return f"<Database '{self.name}'{status}>"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: t.Any):
        if isinstance(other, Database):
            return str(self) == str(other)
        return False

    def __getitem__(self, name: str) -> Database:
        """Retrieve an existing database with the given name."""
        return self.__instances__[name]

    def __delitem__(self, name: str):
        """Delete a database instance by it's name."""
        del self.__instances__[name]

    @classmethod
    def get_default(cls):
        return cls.__instances__["__default__"]

    async def create_pool(self):
        """Create the asyncpg connection pool for this database connection to use."""
        if self.pool:
            self.pool.close()
        if not self.url:
            raise DBError("No database available. Please define a connection with Database.connect.")
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
        """Return generated SQL without executing when Database.execute is used."""
        self._mock = True

    def enable_execution(self):
        """Sets Database.execute to it's normal execution behaviour."""
        self._mock = False

    async def close(self):
        """Close the asyncpg connection pool for this database."""
        if self.pool:
            await self.pool.close()

    async def execute(self, sql: str, *args, timeout: t.Optional[float] = None) -> str:
        """Execute an SQL statement."""
        if self._mock:
            return sql
        if not self.pool:
            await self.create_pool()
        return await self.pool.execute(sql, *args, timeout=timeout)

    def Schema(self, name: str) -> Schema:
        """Return a bound Schema for this database."""
        return Schema(name, self)

    def Table(self, name: str) -> Table:
        """Return a bound Table for the public schema on this database."""
        return Table(name, self)
