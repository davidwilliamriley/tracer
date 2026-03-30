from fastapi import HTTPException


class TracerException(Exception):
    """
    Base class for all application-level exceptions.
    Raise this (or a subclass) anywhere in crud/ or services/
    without importing FastAPI — the handler in main.py converts
    it to an HTTP response automatically.
    """
    def __init__(self, message: str, status_code: int = 400, field: str = None):
        self.message = message
        self.status_code = status_code
        self.field = field
        super().__init__(message)


class NotFoundError(TracerException):
    """Resource does not exist."""
    def __init__(self, resource: str, identifier=None):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(message=detail, status_code=404)


class ConflictError(TracerException):
    """Unique constraint violation — resource already exists."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message=message, status_code=409, field=field)


class ValidationError(TracerException):
    """Business-level validation failure (distinct from Pydantic schema validation)."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message=message, status_code=422, field=field)


class DependencyError(TracerException):
    """Cannot delete a resource because other records depend on it."""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)
