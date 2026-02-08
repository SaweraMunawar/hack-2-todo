"""Database configuration and session management."""

from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)


def create_db_and_tables():
    """Create all SQLModel tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session
