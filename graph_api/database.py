from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

# SQLite requires check_same_thread=False to work with FastAPI's threading model.
# This argument is ignored by other databases (PostgreSQL, MySQL) so it is safe
# to pass unconditionally.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a database session to route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
