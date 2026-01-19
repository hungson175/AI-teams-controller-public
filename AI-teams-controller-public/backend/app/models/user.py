# -*- coding: utf-8 -*-
"""User model for database-backed authentication.

Sprint 25: Database Layer Setup
- User model with email, username, hashed_password
- Timestamps (created_at, updated_at)
- Soft delete support (deleted_at)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user_settings import UserSettings


class User(Base):
    """User model for authentication.

    Attributes:
        id: Primary key
        email: Unique email address (used for login)
        username: Unique display name
        hashed_password: Bcrypt hashed password
        is_active: Whether user can login
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        deleted_at: Soft delete timestamp (None if active)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None, nullable=True)

    # Relationship to settings
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
