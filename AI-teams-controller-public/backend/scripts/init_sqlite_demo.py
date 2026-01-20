#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize SQLite demo database with hardcoded test user.

Sprint 6 Track B: SQLite Conversion
- Creates test/test123 user for demo mode
- Adds default user settings for voice detection
- Idempotent: Safe to run multiple times

Usage:
    cd backend
    python scripts/init_sqlite_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import async_session_maker, engine, init_db
from app.models.user import User
from app.models.user_settings import UserSettings
from passlib.context import CryptContext

# Password hashing context (same as auth_service.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_demo_user() -> None:
    """Create hardcoded test/test123 user with default settings.

    User credentials:
        - Email: test@example.com
        - Username: test
        - Password: test123

    Default settings:
        - Detection mode: silence
        - Stop word: "go go go"
        - Noise filter level: medium
        - Silence duration: 5000ms
        - Theme: system
    """
    print("Initializing SQLite demo database...")

    # Create tables if they don't exist
    await init_db()
    print("✓ Database tables created")

    # Create session
    async with async_session_maker() as session:
        # Check if test user already exists
        from sqlalchemy import select

        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("✓ Demo user already exists (test@example.com)")
            return

        # Hash password
        hashed_password = pwd_context.hash("test123")

        # Create demo user
        demo_user = User(
            email="test@example.com",
            username="test",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(demo_user)
        await session.flush()  # Get user.id before creating settings

        # Create default settings
        demo_settings = UserSettings(
            user_id=demo_user.id,
            detection_mode="silence",
            stop_word="go go go",
            noise_filter_level="medium",
            silence_duration_ms=5000,
            theme="system",
        )
        session.add(demo_settings)

        # Commit transaction
        await session.commit()

        print("✓ Demo user created successfully")
        print("")
        print("Demo credentials:")
        print("  Email: test@example.com")
        print("  Password: test123")
        print("")
        print("Default settings:")
        print("  Detection mode: silence")
        print("  Stop word: go go go")
        print("  Noise filter: medium")
        print("  Silence duration: 5000ms")
        print("  Theme: system")


async def main() -> None:
    """Main entry point."""
    try:
        await create_demo_user()
        print("\n✓ SQLite demo database initialization complete")
    except Exception as e:
        print(f"\n✗ Error initializing demo database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up database connections
        from app.database import close_db

        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
