# -*- coding: utf-8 -*-
"""Voice token generation routes.

Contains endpoints for:
- POST /token/soniox - Soniox API key retrieval
"""

import logging
import os

from fastapi import APIRouter, HTTPException

from app.models.voice_schemas import SonioxTokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/token/soniox", response_model=SonioxTokenResponse)
async def get_soniox_token():
    """Get Soniox API key for frontend speech-to-text.

    Returns the SONIOX_API_KEY from environment for frontend use.
    """
    # Read at runtime (not module-level) for testability
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        logger.error("[VOICE] SONIOX_API_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="SONIOX_API_KEY not configured",
        )

    logger.info("[VOICE] Soniox API key provided")
    return SonioxTokenResponse(api_key=api_key)
