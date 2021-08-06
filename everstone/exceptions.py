class DBError(Exception):
    """Base exception for database errors."""


class QueryError(Exception):
    """Exception for query-specific errors."""


class SchemaError(DBError):
    """Exception for schema-specific errors."""


class ResponseError(DBError):
    """Exception for database response errors."""
