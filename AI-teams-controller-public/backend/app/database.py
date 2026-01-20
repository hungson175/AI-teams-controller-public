# -*- coding: utf-8 -*-
"""Database configuration for async SQLAlchemy 2.0 with SQLite (demo mode).

Sprint 25: Database Layer Setup
- Async engine with aiosqlite driver (demo mode with SQLite)
- Session factory with expire_on_commit=False
- Base model with naming conventions
- Dependency injection for FastAPI

NOTE: For production, use PostgreSQL with asyncpg driver.
"""

import os
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# Load DATABASE_URL from environment
# Default to SQLite for demo mode (easy setup, no external dependencies)
# For production, set DATABASE_URL to PostgreSQL connection string
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./aicontroller.db",  # Local SQLite file for demo
)

# Create async engine with appropriate settings
# Note: SQLite doesn't support pool_size/max_overflow/pool_timeout
if DATABASE_URL.startswith("sqlite"):
    # SQLite settings (no pooling parameters)
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
    )
else:
    # PostgreSQL settings (with connection pooling)
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
    )

# Create session factory with expire_on_commit=False (critical for async)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Naming conventions for constraints (Alembic autogenerate friendly)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Uses AsyncAttrs for async relationship loading.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for FastAPI routes.

    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables.

    NOTE: In production, use Alembic migrations instead.
    This is only for development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections gracefully."""
    await engine.dispose()
