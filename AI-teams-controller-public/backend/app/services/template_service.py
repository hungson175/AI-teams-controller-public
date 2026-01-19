"""Template service for reading and managing team templates."""

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import yaml

from app.models.schemas import TeamTemplate, TemplateRole, CreateTeamResponse
from app.services.template_generator import TemplateGenerator

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing team templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize template service.

        Args:
            templates_dir: Path to templates directory. Defaults to
                PROJECT_ROOT/docs/tmux/templates/
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to project's templates directory
            # backend/app/services/template_service.py -> project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.templates_dir = project_root / "data/templates"

        # Initialize template generator
        self.generator = TemplateGenerator()

    def list_templates(self) -> list[TeamTemplate]:
        """List all available templates.

        Returns:
            List of TeamTemplate objects with metadata.
        """
        templates = []

        if not self.templates_dir.exists():
            return templates

        for entry in self.templates_dir.iterdir():
            if entry.is_dir():
                template_file = entry / "template.yaml"
                if template_file.exists():
                    template = self._load_template(template_file)
                    if template:
                        templates.append(template)

        return templates

    def get_template(self, name: str) -> Optional[TeamTemplate]:
        """Get a specific template by name.

        Args:
            name: Template name (directory name).

        Returns:
            TeamTemplate if found, None otherwise.
        """
        template_dir = self.templates_dir / name
        template_file = template_dir / "template.yaml"

        if not template_file.exists():
            return None

        return self._load_template(template_file)

    def get_template_dir(self, name: str) -> Optional[Path]:
        """Get the directory path for a template.

        Args:
            name: Template name.

        Returns:
            Path to template directory if exists, None otherwise.
        """
        template_dir = self.templates_dir / name
        if template_dir.exists():
            return template_dir
        return None

    def _load_template(self, template_file: Path) -> Optional[TeamTemplate]:
        """Load a template from YAML file.

        Args:
            template_file: Path to template.yaml file.

        Returns:
            TeamTemplate object if valid, None otherwise.
        """
        try:
            with open(template_file, "r") as f:
                data = yaml.safe_load(f)

            roles = []
            for role_data in data.get("roles", []):
                roles.append(
                    TemplateRole(
                        id=role_data["id"],
                        name=role_data["name"],
                        description=role_data.get("description", ""),
                        optional=role_data.get("optional", False),
                    )
                )

            return TeamTemplate(
                name=data["name"],
                display_name=data.get("display_name", data["name"]),
                description=data.get("description", ""),
                version=data.get("version", "1.0.0"),
                roles=roles,
            )
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
            return None

    def create_team(
        self, template_name: str, project_name: str, prd: str
    ) -> CreateTeamResponse:
        """Create a new team from a template.

        Args:
            template_name: Name of the template to use.
            project_name: Name for the new project/team.
            prd: Project Requirements Document content.

        Returns:
            CreateTeamResponse with success status and details.
        """
        # Validate template exists
        template = self.get_template(template_name)
        if not template:
            return CreateTeamResponse(
                success=False,
                team_id="",
                message=f"Template '{template_name}' not found",
                output_dir="",
            )

        template_dir = self.get_template_dir(template_name)
        if not template_dir:
            return CreateTeamResponse(
                success=False,
                team_id="",
                message=f"Template directory not found for '{template_name}'",
                output_dir="",
            )

        # Create output directory matching project structure:
        # ~/dev/tmux-teams/{project_name}/docs/tmux/{project_name}/
        # This matches: AI-teams-controller/docs/tmux/ai_controller_full_team/
        output_base = Path.home() / "dev" / "tmux-teams"
        project_dir = output_base / project_name
        team_dir = project_dir / "docs" / "tmux" / project_name

        try:
            team_dir.mkdir(parents=True, exist_ok=True)

            # Copy prompts folder and replace {prd} placeholders
            prompts_src = template_dir / "prompts"
            prompts_dst = team_dir / "prompts"
            if prompts_src.exists():
                if prompts_dst.exists():
                    shutil.rmtree(prompts_dst)
                shutil.copytree(prompts_src, prompts_dst)

                # Replace {prd} in all prompt files
                for prompt_file in prompts_dst.glob("*.md"):
                    content = prompt_file.read_text()
                    content = content.replace("{prd}", prd)
                    prompt_file.write_text(content)

            # Generate team files in docs/tmux/{project_name}/
            self.generator.generate_readme(team_dir, project_name, template)
            self.generator.generate_whiteboard(team_dir, project_name)
            self.generator.generate_backlog(team_dir, project_name)
            self.generator.generate_setup_script(team_dir, project_name, template)
            # init-role goes at project root
            self.generator.generate_init_role_skill(project_dir, project_name, template)

            # Make setup script executable (already done in generator, but keeping for safety)
            setup_script = team_dir / "setup-team.sh"
            setup_script.chmod(0o755)

            # Run setup-team.sh to create tmux session
            result = subprocess.run(
                [str(setup_script)],
                capture_output=True,
                text=True,
                cwd=str(project_dir),
                timeout=120,
            )

            if result.returncode != 0:
                # Include both stdout and stderr for better debugging
                error_details = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                return CreateTeamResponse(
                    success=False,
                    team_id=project_name,
                    message=f"Setup script failed: {error_details}",
                    output_dir=str(team_dir),
                )

            return CreateTeamResponse(
                success=True,
                team_id=project_name,
                message=f"Team '{project_name}' created successfully",
                output_dir=str(team_dir),
            )

        except Exception as e:
            return CreateTeamResponse(
                success=False,
                team_id=project_name,
                message=f"Failed to create team: {str(e)}",
                output_dir=str(team_dir) if team_dir else "",
            )


# Singleton instance
_template_service: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """Get or create template service singleton."""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
