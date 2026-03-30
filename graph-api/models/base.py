import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.sql import func


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type natively; falls back to CHAR(36) for SQLite.
    Allows the same model code to work across both databases.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(str(value))


class AuditMixin:
    """
    Shared audit columns inherited by all 10 tables.
    created_by / modified_by stored as string (username or user ID).
    Replace with FK to User table when auth is added in Phase 3.
    """
    created_by = Column(String(255), nullable=True)
    created_on = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_by = Column(String(255), nullable=True)
    modified_on = Column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
