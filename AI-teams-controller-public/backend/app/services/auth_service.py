# -*- coding: utf-8 -*-
"""Authentication service with JWT tokens and password hashing.

Sprint 25: Database-backed authentication
- Bcrypt password hashing via passlib
- JWT access tokens (15min) and refresh tokens (7d)
- User registration, login, token refresh
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2880  # 48 hours (2 days * 24 hours * 60 minutes)
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === Password Hashing ===

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    # === JWT Token Management ===

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create a short-lived access token (15 minutes)."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create a long-lived refresh token (7 days)."""
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT token.

        Returns payload dict if valid, None if invalid/expired.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    # === User Operations ===

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def register_user(
        self, email: str, username: str, password: str
    ) -> tuple[User, str, str]:
        """Register a new user.

        Args:
            email: User's email address
            username: User's display name
            password: Plaintext password (will be hashed)

        Returns:
            Tuple of (user, access_token, refresh_token)

        Raises:
            ValueError: If email or username already exists
        """
        # Check for existing email
        if await self.get_user_by_email(email):
            raise ValueError("Email already registered")

        # Check for existing username
        if await self.get_user_by_username(username):
            raise ValueError("Username already taken")

        # Create user with hashed password
        user = User(
            email=email,
            username=username,
            hashed_password=self.hash_password(password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Generate tokens
        access_token = self.create_access_token(user.id, user.email)
        refresh_token = self.create_refresh_token(user.id)

        return user, access_token, refresh_token

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[tuple[User, str, str]]:
        """Authenticate user with email and password.

        Returns:
            Tuple of (user, access_token, refresh_token) if valid, None otherwise
        """
        user = await self.get_user_by_email(email)

        if not user:
            return None

        if not user.is_active:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        # Generate tokens
        access_token = self.create_access_token(user.id, user.email)
        refresh_token = self.create_refresh_token(user.id)

        return user, access_token, refresh_token

    async def refresh_tokens(self, refresh_token: str) -> Optional[tuple[str, str]]:
        """Generate new token pair from valid refresh token.

        Returns:
            Tuple of (new_access_token, new_refresh_token) if valid, None otherwise
        """
        payload = self.decode_token(refresh_token)

        if not payload:
            return None

        if payload.get("type") != "refresh":
            return None

        user_id = int(payload.get("sub", 0))
        user = await self.get_user_by_id(user_id)

        if not user or not user.is_active:
            return None

        # Generate new tokens
        new_access_token = self.create_access_token(user.id, user.email)
        new_refresh_token = self.create_refresh_token(user.id)

        return new_access_token, new_refresh_token

    async def get_current_user(self, access_token: str) -> Optional[User]:
        """Get user from valid access token.

        Returns:
            User if token valid, None otherwise
        """
        payload = self.decode_token(access_token)

        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        user_id = int(payload.get("sub", 0))
        return await self.get_user_by_id(user_id)


def get_auth_service(db: AsyncSession) -> AuthService:
    """Factory function for dependency injection."""
    return AuthService(db)
