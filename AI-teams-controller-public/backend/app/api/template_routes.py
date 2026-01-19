"""API routes for team template management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.models.schemas import (
    TemplatesResponse,
    TeamTemplate,
    CreateTeamRequest,
    CreateTeamResponse,
)
from app.services.template_service import TemplateService, get_template_service

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=TemplatesResponse)
async def list_templates(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TemplateService = Depends(get_template_service),
):
    """List all available team templates. Requires JWT auth."""
    templates = service.list_templates()
    return {"templates": templates}


@router.get("/{template_name}", response_model=TeamTemplate)
async def get_template(
    template_name: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TemplateService = Depends(get_template_service),
):
    """Get a specific template by name. Requires JWT auth."""
    template = service.get_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    return template


@router.post("/create", response_model=CreateTeamResponse)
async def create_team(
    request: CreateTeamRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TemplateService = Depends(get_template_service),
):
    """Create a new team from a template.

    Creates team files in ~/dev/tmux-teams/{project_name}/ and runs setup-team.sh
    to create the tmux session with Claude Code instances.

    Requires JWT auth.
    """
    result = service.create_team(
        template_name=request.template_name,
        project_name=request.project_name,
        prd=request.prd,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result
