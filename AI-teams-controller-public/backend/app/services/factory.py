"""Service factory - Strategy Pattern implementation for swapping services."""

import os
from typing import Literal

from app.services.base import TeamService
from app.services.mock_data import MockDataService
from app.services.tmux_service import tmux_service  # Use singleton, not class


ServiceType = Literal["mock", "tmux"]


def get_service(service_type: ServiceType | None = None) -> TeamService:
    """Get the appropriate service implementation.

    Args:
        service_type: Explicit service type ("mock" or "tmux").
                     If None, reads from TEAM_SERVICE_TYPE env var.
                     Defaults to "tmux" if not specified.

    Returns:
        TeamService implementation
    """
    if service_type is None:
        service_type = os.getenv("TEAM_SERVICE_TYPE", "tmux")

    if service_type == "mock":
        return MockDataService()
    elif service_type == "tmux":
        return tmux_service  # Use singleton with background polling
    else:
        raise ValueError(f"Unknown service type: {service_type}")


# Default service instance - reads from env or defaults to tmux
_service: TeamService | None = None


def get_team_service() -> TeamService:
    """Get the singleton team service instance.

    Uses TEAM_SERVICE_TYPE env var to determine which implementation:
    - "mock": MockDataService (for testing/development)
    - "tmux": TmuxService (for production, default)
    """
    global _service
    if _service is None:
        _service = get_service()
    return _service


def set_team_service(service: TeamService) -> None:
    """Override the team service (useful for testing)."""
    global _service
    _service = service


def reset_team_service() -> None:
    """Reset the singleton to re-read from env."""
    global _service
    _service = None
