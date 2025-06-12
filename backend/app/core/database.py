from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/macro_finance",
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL, echo=True if os.getenv("DEBUG") == "True" else False, future=True
)

# Create async session
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create sync engine for migrations and initial setup
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(SYNC_DATABASE_URL)

# Create sync session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Sync version for initial setup
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Direct sync session for scripts
def get_sync_session():
    """Get a sync session for direct use (not for FastAPI dependency)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables function
def create_tables():
    """Create all tables in the database"""
    # Import all models to ensure they are registered with Base
    from app.models import portfolio, economic_data, user

    Base.metadata.create_all(bind=sync_engine)
