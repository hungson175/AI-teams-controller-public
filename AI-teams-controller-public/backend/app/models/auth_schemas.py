# -*- coding: utf-8 -*-
"""Authentication Pydantic schemas.

Sprint 25: Database-backed authentication
Request/response models for auth endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# === Request Schemas ===


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


# === Response Schemas ===


class UserResponse(BaseModel):
    """User data in responses."""

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthTokens(BaseModel):
    """JWT tokens response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Registration success response."""

    user: UserResponse
    tokens: AuthTokens


class LoginResponse(BaseModel):
    """Login success response."""

    user: UserResponse
    tokens: AuthTokens


class RefreshResponse(BaseModel):
    """Token refresh success response."""

    tokens: AuthTokens


class MeResponse(BaseModel):
    """Current user response."""

    user: UserResponse


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
