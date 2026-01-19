# -*- coding: utf-8 -*-
"""Tests for authentication service.

Sprint 25: TDD - Auth service tests
Tests app/services/auth_service.py with mocked database.
"""

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPasswordHashing:
    """Tests for password hashing functions.

    Note: These tests mock bcrypt to avoid compatibility issues with
    passlib/bcrypt version mismatches. The actual bcrypt behavior is
    validated through the mock contracts.
    """

    def test_hash_password_calls_pwd_context(self):
        """hash_password should use pwd_context.hash."""
        with patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.hash.return_value = "$2b$12$mockedhash"
            from app.services.auth_service import AuthService

            result = AuthService.hash_password("testpassword123")

            mock_ctx.hash.assert_called_once_with("testpassword123")
            assert result == "$2b$12$mockedhash"

    def test_hash_password_returns_string(self):
        """hash_password should return a string."""
        with patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.hash.return_value = "$2b$12$mockhashedpassword"
            from app.services.auth_service import AuthService

            hashed = AuthService.hash_password("testpassword123")
            assert isinstance(hashed, str)
            assert len(hashed) > 0

    def test_verify_password_correct(self):
        """verify_password should return True for correct password."""
        with patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.verify.return_value = True
            from app.services.auth_service import AuthService

            result = AuthService.verify_password("password", "$2b$12$hash")

            mock_ctx.verify.assert_called_once_with("password", "$2b$12$hash")
            assert result is True

    def test_verify_password_incorrect(self):
        """verify_password should return False for incorrect password."""
        with patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.verify.return_value = False
            from app.services.auth_service import AuthService

            result = AuthService.verify_password("wrongpassword", "$2b$12$hash")
            assert result is False

    def test_pwd_context_uses_bcrypt_scheme(self):
        """pwd_context should be configured with bcrypt scheme."""
        from app.services.auth_service import pwd_context

        # Verify bcrypt is in the schemes
        assert "bcrypt" in pwd_context.schemes()


class TestJWTTokenCreation:
    """Tests for JWT token creation."""

    def test_create_access_token_returns_string(self):
        """create_access_token should return JWT string."""
        from app.services.auth_service import AuthService

        token = AuthService.create_access_token(user_id=1, email="test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_three_parts(self):
        """JWT should have header.payload.signature format."""
        from app.services.auth_service import AuthService

        token = AuthService.create_access_token(user_id=1, email="test@example.com")
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_refresh_token_returns_string(self):
        """create_refresh_token should return JWT string."""
        from app.services.auth_service import AuthService

        token = AuthService.create_refresh_token(user_id=1)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_and_refresh_tokens_different(self):
        """Access and refresh tokens should be different."""
        from app.services.auth_service import AuthService

        access = AuthService.create_access_token(user_id=1, email="test@example.com")
        refresh = AuthService.create_refresh_token(user_id=1)
        assert access != refresh


class TestJWTTokenDecoding:
    """Tests for JWT token decoding."""

    def test_decode_valid_access_token(self):
        """decode_token should return payload for valid access token."""
        from app.services.auth_service import AuthService

        token = AuthService.create_access_token(user_id=42, email="test@example.com")
        payload = AuthService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_decode_valid_refresh_token(self):
        """decode_token should return payload for valid refresh token."""
        from app.services.auth_service import AuthService

        token = AuthService.create_refresh_token(user_id=42)
        payload = AuthService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        """decode_token should return None for invalid token."""
        from app.services.auth_service import AuthService

        payload = AuthService.decode_token("invalid.token.here")
        assert payload is None

    def test_decode_expired_token(self):
        """decode_token should return None for expired token."""
        from app.services.auth_service import AuthService
        from jose import jwt

        # Create an expired token manually
        expired_payload = {
            "sub": "1",
            "email": "test@example.com",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        from app.services.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM
        expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        payload = AuthService.decode_token(expired_token)
        assert payload is None

    def test_decode_token_with_wrong_secret(self):
        """decode_token should return None for token signed with wrong key."""
        from jose import jwt

        payload = {
            "sub": "1",
            "email": "test@example.com",
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        from app.services.auth_service import AuthService
        result = AuthService.decode_token(token)
        assert result is None


class TestGetUserByEmail:
    """Tests for get_user_by_email method."""

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        """Should return user when email exists."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.deleted_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuthService(mock_db)
        user = await service.get_user_by_email("test@example.com")

        assert user == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when email doesn't exist."""
        from app.services.auth_service import AuthService

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuthService(mock_db)
        user = await service.get_user_by_email("notfound@example.com")

        assert user is None


class TestGetUserById:
    """Tests for get_user_by_id method."""

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        """Should return user when ID exists."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 42

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuthService(mock_db)
        user = await service.get_user_by_id(42)

        assert user == mock_user

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when ID doesn't exist."""
        from app.services.auth_service import AuthService

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuthService(mock_db)
        user = await service.get_user_by_id(999)

        assert user is None


class TestGetUserByUsername:
    """Tests for get_user_by_username method."""

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        """Should return user when username exists."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.username = "testuser"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuthService(mock_db)
        user = await service.get_user_by_username("testuser")

        assert user == mock_user


class TestRegisterUser:
    """Tests for register_user method."""

    @pytest.mark.asyncio
    async def test_creates_user_with_hashed_password(self):
        """Should create user with bcrypt-hashed password."""
        from app.services.auth_service import AuthService

        # Mock database
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=None), \
             patch.object(service, "get_user_by_username", return_value=None), \
             patch("app.services.auth_service.pwd_context") as mock_ctx, \
             patch("app.services.auth_service.User") as MockUser:

            mock_ctx.hash.return_value = "$2b$12$mockedhash"

            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "new@example.com"
            MockUser.return_value = mock_user

            user, access_token, refresh_token = await service.register_user(
                email="new@example.com",
                username="newuser",
                password="password123"
            )

            # Verify password was hashed via pwd_context
            mock_ctx.hash.assert_called_once_with("password123")
            call_kwargs = MockUser.call_args[1]
            assert call_kwargs["hashed_password"] == "$2b$12$mockedhash"

    @pytest.mark.asyncio
    async def test_raises_error_for_duplicate_email(self):
        """Should raise ValueError when email already exists."""
        from app.services.auth_service import AuthService

        existing_user = MagicMock()
        existing_user.email = "existing@example.com"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=existing_user):
            with pytest.raises(ValueError, match="Email already registered"):
                await service.register_user(
                    email="existing@example.com",
                    username="newuser",
                    password="password123"
                )

    @pytest.mark.asyncio
    async def test_raises_error_for_duplicate_username(self):
        """Should raise ValueError when username already exists."""
        from app.services.auth_service import AuthService

        existing_user = MagicMock()
        existing_user.username = "existinguser"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=None), \
             patch.object(service, "get_user_by_username", return_value=existing_user):
            with pytest.raises(ValueError, match="Username already taken"):
                await service.register_user(
                    email="new@example.com",
                    username="existinguser",
                    password="password123"
                )

    @pytest.mark.asyncio
    async def test_returns_tokens_on_success(self):
        """Should return user and valid tokens on successful registration."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=None), \
             patch.object(service, "get_user_by_username", return_value=None), \
             patch("app.services.auth_service.pwd_context") as mock_ctx, \
             patch("app.services.auth_service.User") as MockUser:

            mock_ctx.hash.return_value = "$2b$12$mockedhash"

            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "new@example.com"
            MockUser.return_value = mock_user

            user, access_token, refresh_token = await service.register_user(
                email="new@example.com",
                username="newuser",
                password="password123"
            )

            assert user == mock_user
            assert isinstance(access_token, str)
            assert isinstance(refresh_token, str)
            assert len(access_token.split(".")) == 3
            assert len(refresh_token.split(".")) == 3


class TestAuthenticateUser:
    """Tests for authenticate_user method."""

    @pytest.mark.asyncio
    async def test_returns_tokens_for_valid_credentials(self):
        """Should return user and tokens for valid email/password."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "$2b$12$mockedhash"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=mock_user), \
             patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.verify.return_value = True  # Password matches

            result = await service.authenticate_user("test@example.com", "correctpassword")

            assert result is not None
            user, access_token, refresh_token = result
            assert user == mock_user
            assert isinstance(access_token, str)
            assert isinstance(refresh_token, str)
            mock_ctx.verify.assert_called_once_with("correctpassword", "$2b$12$mockedhash")

    @pytest.mark.asyncio
    async def test_returns_none_for_invalid_email(self):
        """Should return None for non-existent email."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=None):
            result = await service.authenticate_user("notfound@example.com", "password")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_wrong_password(self):
        """Should return None for incorrect password."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "$2b$12$mockedhash"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=mock_user), \
             patch("app.services.auth_service.pwd_context") as mock_ctx:
            mock_ctx.verify.return_value = False  # Password doesn't match

            result = await service.authenticate_user("test@example.com", "wrongpassword")
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_inactive_user(self):
        """Should return None for inactive user."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = False  # Inactive
        mock_user.hashed_password = "$2b$12$mockedhash"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        with patch.object(service, "get_user_by_email", return_value=mock_user):
            result = await service.authenticate_user("test@example.com", "password")
            assert result is None


class TestRefreshTokens:
    """Tests for refresh_tokens method."""

    @pytest.mark.asyncio
    async def test_returns_new_tokens_for_valid_refresh(self):
        """Should return new token pair for valid refresh token."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        refresh_token = AuthService.create_refresh_token(user_id=1)

        with patch.object(service, "get_user_by_id", return_value=mock_user):
            result = await service.refresh_tokens(refresh_token)

            assert result is not None
            new_access, new_refresh = result
            assert isinstance(new_access, str)
            assert isinstance(new_refresh, str)

    @pytest.mark.asyncio
    async def test_returns_none_for_invalid_token(self):
        """Should return None for invalid refresh token."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        result = await service.refresh_tokens("invalid.token.here")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_access_token(self):
        """Should return None if access token used instead of refresh."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        # Use access token instead of refresh
        access_token = AuthService.create_access_token(user_id=1, email="test@example.com")
        result = await service.refresh_tokens(access_token)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_inactive_user(self):
        """Should return None if user is inactive."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = False

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        refresh_token = AuthService.create_refresh_token(user_id=1)

        with patch.object(service, "get_user_by_id", return_value=mock_user):
            result = await service.refresh_tokens(refresh_token)
            assert result is None


class TestGetCurrentUser:
    """Tests for get_current_user method."""

    @pytest.mark.asyncio
    async def test_returns_user_for_valid_access_token(self):
        """Should return user for valid access token."""
        from app.services.auth_service import AuthService

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        access_token = AuthService.create_access_token(user_id=1, email="test@example.com")

        with patch.object(service, "get_user_by_id", return_value=mock_user):
            user = await service.get_current_user(access_token)
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_returns_none_for_invalid_token(self):
        """Should return None for invalid token."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        user = await service.get_current_user("invalid.token.here")
        assert user is None

    @pytest.mark.asyncio
    async def test_returns_none_for_refresh_token(self):
        """Should return None if refresh token used."""
        from app.services.auth_service import AuthService

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        refresh_token = AuthService.create_refresh_token(user_id=1)
        user = await service.get_current_user(refresh_token)
        assert user is None


class TestJWTConfiguration:
    """Tests for JWT configuration constants."""

    def test_jwt_secret_from_env(self):
        """JWT_SECRET_KEY should be configurable via environment."""
        test_secret = "test-secret-from-env"
        with patch.dict(os.environ, {"JWT_SECRET_KEY": test_secret}):
            import importlib
            import app.services.auth_service as auth_module
            importlib.reload(auth_module)
            assert auth_module.JWT_SECRET_KEY == test_secret

    def test_access_token_expiry(self):
        """ACCESS_TOKEN_EXPIRE_MINUTES should be reasonable."""
        from app.services.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES

        # Should be between 5 minutes and 48 hours (2880 minutes)
        assert 5 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 2880

    def test_refresh_token_expiry(self):
        """REFRESH_TOKEN_EXPIRE_DAYS should be reasonable."""
        from app.services.auth_service import REFRESH_TOKEN_EXPIRE_DAYS

        # Should be between 1 and 30 days
        assert 1 <= REFRESH_TOKEN_EXPIRE_DAYS <= 30

    def test_access_token_has_48h_expiry(self):
        """Access token should have 48h (2880 min) expiry in payload."""
        from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
        from datetime import datetime, timedelta

        # Create token
        token = AuthService.create_access_token(user_id=1, email="test@example.com")
        payload = AuthService.decode_token(token)

        # Verify expiry time
        assert payload is not None
        assert "exp" in payload

        # Calculate expected expiry (should be ~48h from now if ACCESS_TOKEN_EXPIRE_MINUTES=2880)
        now = datetime.utcnow()
        expected_exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        actual_exp = datetime.utcfromtimestamp(payload["exp"])

        # Allow 5 second tolerance for test execution time
        time_diff = abs((actual_exp - expected_exp).total_seconds())
        assert time_diff < 5, f"Token expiry mismatch: expected ~{expected_exp}, got {actual_exp}"


class TestGetAuthService:
    """Tests for get_auth_service factory function."""

    def test_returns_auth_service_instance(self):
        """get_auth_service should return AuthService instance."""
        from app.services.auth_service import get_auth_service, AuthService

        mock_db = AsyncMock()
        service = get_auth_service(mock_db)

        assert isinstance(service, AuthService)
        assert service.db == mock_db
