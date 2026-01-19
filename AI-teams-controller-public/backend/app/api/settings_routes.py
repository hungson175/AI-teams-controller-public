# -*- coding: utf-8 -*-
"""Settings routes for user preferences.

Sprint 25: Settings API
- GET /api/settings - Get user settings
- PUT /api/settings - Update user settings
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_routes import get_current_user_from_token
from app.database import get_db
from app.models.auth_schemas import UserResponse
from app.models.user_settings import UserSettings

router = APIRouter(prefix="/api/settings", tags=["settings"])


# === Enums for validation ===


class DetectionMode(str, Enum):
    """Valid detection modes."""

    SILENCE = "silence"
    STOPWORD = "stopword"


class NoiseFilterLevel(str, Enum):
    """Valid noise filter levels."""

    VERY_LOW = "very-low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very-high"


class Theme(str, Enum):
    """Valid theme options."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


# === Schemas ===


class SettingsUpdateRequest(BaseModel):
    """Request schema for updating settings (all fields optional)."""

    detection_mode: Optional[DetectionMode] = None
    stop_word: Optional[str] = Field(None, max_length=50)
    noise_filter_level: Optional[NoiseFilterLevel] = None
    silence_duration_ms: Optional[int] = Field(None, ge=0, le=30000)
    theme: Optional[Theme] = None


class SettingsResponse(BaseModel):
    """Response schema for settings."""

    detection_mode: str
    stop_word: str
    noise_filter_level: str
    silence_duration_ms: int
    theme: str
    updated_at: datetime

    model_config = {"from_attributes": True}


# === Helper Functions ===


async def get_user_settings(
    db: AsyncSession, user_id: int
) -> Optional[UserSettings]:
    """Get user settings from database.

    Args:
        db: Database session
        user_id: User ID to get settings for

    Returns:
        UserSettings if found, None otherwise
    """
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_default_settings(
    db: AsyncSession, user_id: int
) -> UserSettings:
    """Create default settings for a user.

    Args:
        db: Database session
        user_id: User ID to create settings for

    Returns:
        Newly created UserSettings with defaults
    """
    settings = UserSettings(
        user_id=user_id,
        detection_mode="silence",
        stop_word="go go go",
        noise_filter_level="medium",
        silence_duration_ms=5000,
        theme="system",
    )
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


async def update_user_settings(
    db: AsyncSession, user_id: int, updates: SettingsUpdateRequest
) -> UserSettings:
    """Update user settings in database.

    Args:
        db: Database session
        user_id: User ID to update settings for
        updates: Partial update data

    Returns:
        Updated UserSettings
    """
    # Get existing settings or create defaults
    settings = await get_user_settings(db, user_id)
    if not settings:
        settings = await create_default_settings(db, user_id)

    # Apply partial updates
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            # Convert enum to string value
            if hasattr(value, "value"):
                value = value.value
            setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return settings


# === Endpoints ===


@router.get(
    "",
    response_model=SettingsResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_settings(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SettingsResponse:
    """Get current user's settings.

    Returns settings if they exist, or creates and returns defaults.
    """
    settings = await get_user_settings(db, current_user.id)

    if not settings:
        settings = await create_default_settings(db, current_user.id)

    return SettingsResponse.model_validate(settings)


@router.put(
    "",
    response_model=SettingsResponse,
    responses={
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
async def update_settings(
    request: SettingsUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SettingsResponse:
    """Update current user's settings.

    Supports partial updates - only provided fields are updated.
    """
    settings = await update_user_settings(db, current_user.id, request)
    return SettingsResponse.model_validate(settings)
