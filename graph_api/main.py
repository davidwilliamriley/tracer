from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

import models  # registers all models with Base.metadata
from database import engine, Base
from exceptions import TracerException
from schemas.error import FieldError, ValidationErrorResponse
from routers import (
    graph,
    node_type,
    edge_type,
    node_property_definition,
    edge_property_definition,
    node_type_property_assignment,
    edge_type_property_assignment,
    node,
    edge,
    node_property_value,
    edge_property_value,
)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Tracer Graph API",
    description="Property graph database API for railway programme governance.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS
# Replace the wildcard origin with specific origins before deployment.
# e.g. allow_origins=["http://localhost:3000", "https://yourapp.com"]
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(TracerException)
async def tracer_exception_handler(request: Request, exc: TracerException):
    """
    Handles all application-level exceptions raised in crud/ and services/.
    Converts TracerException (and subclasses) to a uniform error response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "field": exc.field,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic schema validation errors (422).
    Converts FastAPI's nested format into a flat list of field errors.
    """
    field_errors = []
    for error in exc.errors():
        loc_parts = [str(l) for l in error["loc"] if l != "body"]
        field = ".".join(loc_parts) if loc_parts else "unknown"
        field_errors.append(FieldError(field=field, message=error["msg"]))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ValidationErrorResponse(errors=field_errors).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unhandled exceptions.
    Never exposes stack traces to the client.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred.",
            "field": None,
            "status_code": 500,
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Layer 1 — type registry
app.include_router(node_type.router)
app.include_router(edge_type.router)

# Layer 2 — schema / property definitions and assignments
app.include_router(node_property_definition.router)
app.include_router(edge_property_definition.router)
app.include_router(node_type_property_assignment.router)
app.include_router(edge_type_property_assignment.router)

# Layer 3 — instance data
app.include_router(graph.router)
app.include_router(node.router)
app.include_router(edge.router)
app.include_router(node_property_value.router)
app.include_router(edge_property_value.router)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "api": "Tracer Graph API", "version": "0.1.0"}
