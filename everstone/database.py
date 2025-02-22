from __future__ import annotations

import contextlib
import json
import logging
import typing as t
from contextvars import ContextVar

import asyncpg

from .bases import LimitInstances
from .exceptions import DBError
from .sql import types
from .sql.schema import Schema
from .sql.table import Table

log = logging.getLogger(__name__)


class Database(LimitInstances):
    """Represents a database."""

    __instances__: dict[str, Database]

    def __init__(self, name: str):
        self.name = name
        self.user: t.Optional[str] = None
        self.url: t.Optional[str] = None

        self.pool: t.Optional[asyncpg.Pool] = None

        self.type = types
        self.schemas: t.Set[Schema] = set()

        self._mock = False
        self._prepared = False
        self._tracking = ContextVar(f"stmt_tracking:{name}")

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
            return f"<Database '{self.name}' user='{self.user}'{status}>"
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
            raise DBError("Please define a connection with Database.connect.")
        self.pool = await asyncpg.create_pool(self.url, init=self._enable_json)  # pragma: no cover

    @staticmethod
    async def _enable_json(conn: asyncpg.Connection):  # pragma: no cover
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

    @contextlib.contextmanager
    def stmt_tracking(self):
        """Collects raw executed statements until exit when execution is disabled."""
        ctx_token = self._tracking.set([])
        try:
            yield self
        finally:
            self._tracking.reset(ctx_token)

    async def close(self):  # pragma: no cover
        """Close the asyncpg connection pool for this database."""
        if self.pool:
            await self.pool.close()

    async def execute(self, sql: str, *args, timeout: t.Optional[float] = None) -> t.Union[str, tuple[str, t.Any]]:
        """Execute an SQL statement."""
        if self._mock:
            try:
                stmt_list = self._tracking.get()
                stmt_list.append((sql, args))
            except LookupError:
                pass
            if not args:
                return sql
            else:
                return sql, *args

        if not self.pool:  # pragma: no cover
            await self.create_pool()
        return await self.pool.execute(sql, *args, timeout=timeout)  # pragma: no cover

    def Schema(self, name: str) -> Schema:
        """Return a bound Schema for this database."""
        s = Schema(name, self)
        self.schemas.add(s)
        return s

    def Table(self, name: str) -> Table:
        """Return a bound Table for the public schema on this database."""
        return Table(name, self)
