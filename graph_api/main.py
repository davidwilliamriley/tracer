from fastapi import FastAPI
from database import Base, engine
from models import NodeType
from routers import node_type

# Create all Tables on STartup (replace with Alembic for Production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Graph API", version="0.1.0")

app.include_router(node_type.router)
