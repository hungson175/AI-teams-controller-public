# -*- coding: utf-8 -*-
"""Authentication routes with database-backed JWT auth.

Sprint 25: Database-backed authentication
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login with email/password
- POST /api/auth/refresh - Refresh access token
- POST /api/auth/logout - Logout (client-side token removal)
- GET /api/auth/me - Get current user info
"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.auth_schemas import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    MeResponse,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
    AuthTokens,
)
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

# HTTP Bearer security scheme for JWT tokens
security = HTTPBearer(auto_error=False)


# === Dependency Helpers ===


async def get_current_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Extract and validate user from JWT token.

    Raises HTTPException 401 if token invalid/missing.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = get_auth_service(db)
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse.model_validate(user)


# === Auth Endpoints ===


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Email or username already exists"},
        403: {"model": ErrorResponse, "description": "Registration disabled"},
    },
)
async def register(
    request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RegisterResponse:
    """Register a new user.

    P0 SECURITY: Registration DISABLED.
    Only Boss can add users via database directly.
    """
    # P0 SECURITY: Public registration disabled - deadly security risk
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public registration is disabled. Contact system administrator to create an account.",
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """Login with email and password.

    Returns JWT access and refresh tokens on success.
    """
    auth_service = get_auth_service(db)

    result = await auth_service.authenticate_user(
        email=request.email,
        password=request.password,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user, access_token, refresh_token = result

    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshResponse:
    """Refresh access token using refresh token.

    Returns new access and refresh token pair.
    """
    auth_service = get_auth_service(db)

    result = await auth_service.refresh_tokens(request.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    access_token, refresh_token = result

    return RefreshResponse(
        tokens=AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout() -> MessageResponse:
    """Logout user.

    JWT tokens are stateless, so logout is handled client-side
    by discarding the tokens. This endpoint confirms the action.
    """
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=MeResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
) -> MeResponse:
    """Get current authenticated user info."""
    return MeResponse(user=current_user)


# === Legacy Simple Auth (for backwards compatibility) ===

# Keep SESSION_TOKEN for old clients during migration
SESSION_TOKEN = "simple-session-token"


@router.post("/login/simple", include_in_schema=False)
async def login_simple(request: LoginRequest):
    """Legacy simple login (env-var based).

    Deprecated: Use /api/auth/login instead.
    """
    auth_email = os.environ.get("AUTH_EMAIL")
    auth_password = os.environ.get("AUTH_PASSWORD")

    if not auth_email or not auth_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth credentials not configured on server",
        )

    if request.email == auth_email and request.password == auth_password:
        return {"success": True, "token": SESSION_TOKEN}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )
