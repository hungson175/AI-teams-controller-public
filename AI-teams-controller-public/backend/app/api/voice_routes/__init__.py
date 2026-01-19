# -*- coding: utf-8 -*-
"""Voice command REST API routes (split into modules).

This package combines three sub-routers:
- token_routes: Token generation for OpenAI and Soniox
- command_routes: Command processing, transcription, and helper functions
- task_routes: Task completion (Stop hook) and WebSocket feedback
"""

from fastapi import APIRouter

from .command_routes import router as command_router
from .task_routes import router as task_router
from .token_routes import router as token_router

# Combined router with all voice operations
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Include all sub-routers
router.include_router(token_router)
router.include_router(command_router)
router.include_router(task_router)

__all__ = ["router"]
