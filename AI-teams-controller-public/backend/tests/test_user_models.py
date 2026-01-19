# -*- coding: utf-8 -*-
"""Tests for User model.

Sprint 25: TDD - User model tests
Tests app/models/user.py without real database connections.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestUserModelDefinition:
    """Tests for User model structure and definition."""

    def test_user_tablename(self):
        """User model should have correct __tablename__."""
        from app.models.user import User

        assert User.__tablename__ == "users"

    def test_user_has_id_column(self):
        """User model should have id primary key column."""
        from app.models.user import User

        assert hasattr(User, "id")
        # Check it's a primary key via column info
        mapper = User.__mapper__
        pk_cols = [col.name for col in mapper.primary_key]
        assert "id" in pk_cols

    def test_user_has_email_column(self):
        """User model should have email column with constraints."""
        from app.models.user import User

        assert hasattr(User, "email")
        # Verify column exists in mapper
        mapper = User.__mapper__
        email_col = mapper.columns.get("email")
        assert email_col is not None
        assert email_col.nullable is False
        assert email_col.unique is True

    def test_user_has_username_column(self):
        """User model should have username column with constraints."""
        from app.models.user import User

        assert hasattr(User, "username")
        mapper = User.__mapper__
        username_col = mapper.columns.get("username")
        assert username_col is not None
        assert username_col.nullable is False
        assert username_col.unique is True

    def test_user_has_hashed_password_column(self):
        """User model should have hashed_password column."""
        from app.models.user import User

        assert hasattr(User, "hashed_password")
        mapper = User.__mapper__
        pw_col = mapper.columns.get("hashed_password")
        assert pw_col is not None
        assert pw_col.nullable is False

    def test_user_has_is_active_column(self):
        """User model should have is_active boolean column."""
        from app.models.user import User

        assert hasattr(User, "is_active")
        mapper = User.__mapper__
        active_col = mapper.columns.get("is_active")
        assert active_col is not None

    def test_user_has_created_at_column(self):
        """User model should have created_at timestamp column."""
        from app.models.user import User

        assert hasattr(User, "created_at")
        mapper = User.__mapper__
        col = mapper.columns.get("created_at")
        assert col is not None
        assert col.nullable is False

    def test_user_has_updated_at_column(self):
        """User model should have updated_at timestamp column."""
        from app.models.user import User

        assert hasattr(User, "updated_at")
        mapper = User.__mapper__
        col = mapper.columns.get("updated_at")
        assert col is not None
        assert col.nullable is False

    def test_user_has_deleted_at_column_for_soft_delete(self):
        """User model should have deleted_at for soft delete support."""
        from app.models.user import User

        assert hasattr(User, "deleted_at")
        mapper = User.__mapper__
        col = mapper.columns.get("deleted_at")
        assert col is not None
        assert col.nullable is True  # Must be nullable for soft delete


class TestUserModelInheritance:
    """Tests for User model inheritance."""

    def test_user_inherits_from_declarative_base(self):
        """User should inherit from SQLAlchemy DeclarativeBase."""
        from sqlalchemy.orm import DeclarativeBase
        from app.models.user import User

        # Check that User has the table attribute (marker of declarative model)
        assert hasattr(User, "__tablename__")
        assert hasattr(User, "__mapper__")
        # User's __mro__ should include a DeclarativeBase subclass
        assert any(
            issubclass(base, DeclarativeBase)
            for base in User.__mro__
            if base is not object and base is not User
        )


class TestUserModelDefaults:
    """Tests for User model default values."""

    def test_is_active_default_true(self):
        """is_active should default to True."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("is_active")
        # Check column has default
        assert col.default is not None
        assert col.default.arg is True

    def test_deleted_at_default_none(self):
        """deleted_at should default to None (via nullable=True)."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("deleted_at")
        # Check column allows None (nullable) - this is how soft delete works
        assert col.nullable is True
        # When nullable=True and no explicit default, SQLAlchemy treats None as default


class TestUserModelRepr:
    """Tests for User model __repr__ method."""

    def test_repr_method_exists(self):
        """User model should have custom __repr__ method."""
        from app.models.user import User

        # Check that __repr__ is defined on the class (not inherited default)
        assert hasattr(User, "__repr__")
        # Verify it's explicitly defined, not just inherited
        assert "__repr__" in User.__dict__

    def test_repr_implementation_format(self):
        """__repr__ should return expected format with id, email, username."""
        from app.models.user import User
        import inspect

        # Get the source code of __repr__ to verify it has the right format
        source = inspect.getsource(User.__repr__)

        # Should include id, email, and username in the format string
        assert "self.id" in source
        assert "self.email" in source
        assert "self.username" in source
        assert "<User(" in source

    def test_repr_returns_string(self):
        """__repr__ return type annotation should be str."""
        from app.models.user import User
        import inspect

        sig = inspect.signature(User.__repr__)
        # Check return annotation if present
        if sig.return_annotation != inspect.Parameter.empty:
            assert sig.return_annotation == str


class TestUserModelColumnLengths:
    """Tests for column string lengths."""

    def test_email_max_length(self):
        """email column should have appropriate max length."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("email")
        # Email should accommodate standard lengths
        assert col.type.length >= 255

    def test_username_max_length(self):
        """username column should have appropriate max length."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("username")
        assert col.type.length >= 50  # At least 50 chars

    def test_hashed_password_max_length(self):
        """hashed_password should accommodate bcrypt hashes."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("hashed_password")
        # Bcrypt hashes are 60 chars, but allow more for flexibility
        assert col.type.length >= 60


class TestUserModelIndexes:
    """Tests for User model indexes."""

    def test_email_is_indexed(self):
        """email column should have an index for fast lookups."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("email")
        assert col.index is True

    def test_username_is_indexed(self):
        """username column should have an index for fast lookups."""
        from app.models.user import User

        mapper = User.__mapper__
        col = mapper.columns.get("username")
        assert col.index is True
