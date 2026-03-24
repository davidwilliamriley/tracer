from pydantic import BaseModel
from typing import Optional, List


class ErrorDetail(BaseModel):
    """
    Standard error response returned by every non-2xx response.

    Shape:
        {
            "error": "NotFoundError",
            "message": "NodeType 'SAFETY_REQUIREMENT' not found",
            "field": null,           -- populated for field-level validation errors
            "status_code": 404
        }

    For Pydantic validation errors (422), multiple field errors are
    returned in the `errors` list instead.
    """
    error: str
    message: str
    field: Optional[str] = None
    status_code: int


class FieldError(BaseModel):
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    error: str = "ValidationError"
    message: str = "Request validation failed"
    status_code: int = 422
    errors: List[FieldError]
