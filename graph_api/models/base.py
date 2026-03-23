import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR
from database import Base


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
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
        return uuid.UUID(value)


class AuditMixin:
    created_by = Column(String(255), nullable=True)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_by = Column(String(255), nullable=True)
    modified_on = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)