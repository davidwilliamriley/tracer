from fastapi import FastAPI
from database import engine
import models  # ensures all models are registered with Base.metadata
from database import Base
from routers import (
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

# Create all tables on startup.
# Replace with Alembic migrations in Phase 3.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tracer Graph API",
    description="Property Graph DB API.",
    version="0.1.0",
)

# Layer 1 — type registry
app.include_router(node_type.router)
app.include_router(edge_type.router)

# Layer 2 — schema / property definitions and assignments
app.include_router(node_property_definition.router)
app.include_router(edge_property_definition.router)
app.include_router(node_type_property_assignment.router)
app.include_router(edge_type_property_assignment.router)

# Layer 3 — instance data
app.include_router(node.router)
app.include_router(edge.router)
app.include_router(node_property_value.router)
app.include_router(edge_property_value.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "api": "Tracer Graph API", "version": "0.1.0"}
