#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Admin script to create test users for QA.

Usage:
    uv run python scripts/create_test_user.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import async_session_maker, init_db
from app.models.user import User
from app.models.user_settings import UserSettings  # Import to resolve relationship
from app.services.auth_service import AuthService


async def create_test_user():
    """Create test user: test@test.com / testpass123."""

    # Initialize database tables
    await init_db()

    async with async_session_maker() as db:
        # Check if user already exists
        auth_service = AuthService(db)
        existing_user = await auth_service.get_user_by_email("test@test.com")

        if existing_user:
            print("✅ Test user already exists:")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            print(f"   Active: {existing_user.is_active}")
            return

        # Create new test user
        hashed_password = AuthService.hash_password("testpass123")

        new_user = User(
            email="test@test.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        print("✅ Test user created successfully!")
        print(f"   Email: {new_user.email}")
        print(f"   Username: {new_user.username}")
        print(f"   Password: testpass123")
        print(f"   Active: {new_user.is_active}")
        print(f"   ID: {new_user.id}")


if __name__ == "__main__":
    asyncio.run(create_test_user())
