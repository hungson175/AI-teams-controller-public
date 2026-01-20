# -*- coding: utf-8 -*-
"""Tests for database configuration module.

Sprint 25: TDD - Database layer tests
Tests database.py without real database connections.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestDatabaseConfiguration:
    """Tests for database configuration and constants."""

    def test_database_url_from_environment(self):
        """DATABASE_URL should be read from environment variable."""
        test_url = "sqlite+aiosqlite:///./test.db"
        with patch.dict(os.environ, {"DATABASE_URL": test_url}):
            # Re-import to pick up new env var
            import importlib
            import app.database as db_module
            importlib.reload(db_module)
            assert db_module.DATABASE_URL == test_url

    def test_database_url_default(self):
        """DATABASE_URL should have sensible default when not in env."""
        # Remove DATABASE_URL from environment if present
        env_without_db = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
        with patch.dict(os.environ, env_without_db, clear=True):
            import importlib
            import app.database as db_module
            importlib.reload(db_module)
            assert "sqlite+aiosqlite://" in db_module.DATABASE_URL
            assert "aicontroller.db" in db_module.DATABASE_URL

    def test_naming_convention_has_required_keys(self):
        """NAMING_CONVENTION should have all standard constraint prefixes."""
        from app.database import NAMING_CONVENTION

        required_keys = ["ix", "uq", "ck", "fk", "pk"]
        for key in required_keys:
            assert key in NAMING_CONVENTION, f"Missing naming convention for {key}"

    def test_naming_convention_uses_table_name(self):
        """Naming conventions should include table name for clarity."""
        from app.database import NAMING_CONVENTION

        # pk, uq, ck, fk should all reference table_name
        for key in ["pk", "uq", "ck", "fk"]:
            assert "table_name" in NAMING_CONVENTION[key], f"{key} should include table_name"


class TestBaseModel:
    """Tests for Base declarative class."""

    def test_base_inherits_async_attrs(self):
        """Base class should support async attribute loading."""
        from sqlalchemy.ext.asyncio import AsyncAttrs
        from app.database import Base

        assert issubclass(Base, AsyncAttrs)

    def test_base_has_metadata_with_naming_convention(self):
        """Base.metadata should have naming convention applied."""
        from app.database import Base, NAMING_CONVENTION

        assert Base.metadata.naming_convention == NAMING_CONVENTION


class TestGetDb:
    """Tests for get_db dependency function."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """get_db should yield an AsyncSession."""
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_session_maker = MagicMock(return_value=mock_session)

        with patch("app.database.async_session_maker", mock_session_maker):
            from app.database import get_db

            # get_db is an async generator, need to iterate
            gen = get_db()
            session = await gen.__anext__()

            assert session == mock_session
            mock_session_maker.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_session_is_context_managed(self):
        """get_db should use session as context manager."""
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_session_maker = MagicMock(return_value=mock_session)

        with patch("app.database.async_session_maker", mock_session_maker):
            from app.database import get_db

            # Consume the generator fully
            gen = get_db()
            session = await gen.__anext__()
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            # Context manager should have been entered
            mock_session.__aenter__.assert_called_once()


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """init_db should call create_all on Base.metadata."""
        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine_context = AsyncMock()
        mock_engine_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine_context.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=mock_engine_context)

        with patch("app.database.engine", mock_engine):
            from app.database import init_db
            await init_db()

            mock_engine.begin.assert_called_once()
            mock_conn.run_sync.assert_called_once()


class TestCloseDb:
    """Tests for close_db function."""

    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        """close_db should call engine.dispose()."""
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()

        with patch("app.database.engine", mock_engine):
            from app.database import close_db
            await close_db()

            mock_engine.dispose.assert_called_once()


class TestEngineConfiguration:
    """Tests for async engine configuration."""

    def test_async_session_maker_exists(self):
        """async_session_maker should be configured."""
        from app.database import async_session_maker

        assert async_session_maker is not None

    def test_engine_exists(self):
        """engine should be configured."""
        from app.database import engine

        assert engine is not None
