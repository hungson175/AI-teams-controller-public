# -*- coding: utf-8 -*-
"""UserSettings model for user preferences and voice settings.

Sprint 25: Database Layer Setup
- User settings with voice preferences
- Detection mode, stop word, noise filter
- Theme preferences
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserSettings(Base):
    """User settings model for preferences storage.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (unique - one settings per user)
        detection_mode: Voice detection mode (silence or stopword)
        stop_word: Stop word for voice detection
        noise_filter_level: Noise filter level
        silence_duration_ms: Silence duration in milliseconds
        theme: UI theme preference
        created_at: Settings creation timestamp
        updated_at: Last modification timestamp
    """

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Voice settings
    detection_mode: Mapped[str] = mapped_column(
        String(20), default="silence"
    )
    stop_word: Mapped[str] = mapped_column(
        String(50), default="go go go"
    )
    noise_filter_level: Mapped[str] = mapped_column(
        String(20), default="medium"
    )
    silence_duration_ms: Mapped[int] = mapped_column(
        Integer, default=5000
    )

    # UI preferences
    theme: Mapped[str] = mapped_column(
        String(20), default="system"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id}, theme={self.theme})>"
