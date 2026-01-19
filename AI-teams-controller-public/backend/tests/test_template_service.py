# -*- coding: utf-8 -*-
"""Tests for template_service.py.

Tests the TemplateService class for:
1. list_templates - returns available templates
2. get_template - returns specific template
3. get_template - returns None for missing template
4. create_team - success path (mocked subprocess)
5. create_team - failure path (mocked subprocess failure)
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from app.services.template_service import TemplateService
from app.models.schemas import CreateTeamResponse


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def temp_templates_dir():
    """Create a temporary templates directory with test templates."""
    temp_dir = tempfile.mkdtemp()
    templates_dir = Path(temp_dir) / "templates"
    templates_dir.mkdir()

    # Create 'minimal' template
    minimal_dir = templates_dir / "minimal"
    minimal_dir.mkdir()
    (minimal_dir / "template.yaml").write_text(
        yaml.dump(
            {
                "name": "minimal",
                "display_name": "Minimal Team",
                "description": "A minimal 2-person team",
                "version": "1.0.0",
                "roles": [
                    {"id": "PM", "name": "Project Manager", "description": "Coordinates work"},
                    {"id": "CODER", "name": "Coder", "description": "Writes code"},
                ],
            }
        )
    )
    prompts_dir = minimal_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "PM.md").write_text("# PM\n\n{prd}\n\nManage the project.")
    (prompts_dir / "CODER.md").write_text("# CODER\n\n{prd}\n\nWrite the code.")

    # Create 'standard' template
    standard_dir = templates_dir / "standard"
    standard_dir.mkdir()
    (standard_dir / "template.yaml").write_text(
        yaml.dump(
            {
                "name": "standard",
                "display_name": "Standard Team",
                "description": "A standard 3-person team",
                "version": "1.0.0",
                "roles": [
                    {"id": "PM", "name": "Project Manager", "description": "Coordinates work"},
                    {"id": "DEV", "name": "Developer", "description": "Implements features"},
                    {"id": "QA", "name": "QA Engineer", "description": "Tests the code"},
                ],
            }
        )
    )
    prompts_dir = standard_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "PM.md").write_text("# PM\n\n{prd}\n\nManage the project.")
    (prompts_dir / "DEV.md").write_text("# DEV\n\n{prd}\n\nDevelop features.")
    (prompts_dir / "QA.md").write_text("# QA\n\n{prd}\n\nTest everything.")

    yield templates_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for team creation.

    Creates structure: temp_dir/dev/tmux-teams/ to match Path.home() / "dev/tmux-teams"
    """
    temp_dir = tempfile.mkdtemp()
    output_dir = Path(temp_dir) / "dev" / "tmux-teams"
    output_dir.mkdir(parents=True)

    yield temp_dir  # Return base dir for Path.home() mock

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def template_service(temp_templates_dir):
    """Create TemplateService with temp directory."""
    return TemplateService(templates_dir=str(temp_templates_dir))


# ============================================================
# Test: list_templates
# ============================================================


def test_list_templates_returns_both_templates(template_service):
    """list_templates should return both templates."""
    templates = template_service.list_templates()

    assert len(templates) == 2
    names = {t.name for t in templates}
    assert "minimal" in names
    assert "standard" in names


def test_list_templates_empty_dir():
    """list_templates should return empty list for non-existent directory."""
    service = TemplateService(templates_dir="/nonexistent/path")
    templates = service.list_templates()

    assert templates == []


def test_list_templates_correct_fields(template_service):
    """list_templates should return templates with correct fields."""
    templates = template_service.list_templates()

    minimal = next(t for t in templates if t.name == "minimal")
    assert minimal.display_name == "Minimal Team"
    assert minimal.description == "A minimal 2-person team"
    assert minimal.version == "1.0.0"
    assert len(minimal.roles) == 2


# ============================================================
# Test: get_template
# ============================================================


def test_get_template_returns_correct_template(template_service):
    """get_template should return the correct template."""
    template = template_service.get_template("minimal")

    assert template is not None
    assert template.name == "minimal"
    assert template.display_name == "Minimal Team"
    assert len(template.roles) == 2


def test_get_template_returns_none_for_missing(template_service):
    """get_template should return None for missing template."""
    template = template_service.get_template("nonexistent")

    assert template is None


def test_get_template_roles_correct(template_service):
    """get_template should return template with correct roles."""
    template = template_service.get_template("standard")

    assert template is not None
    role_ids = [r.id for r in template.roles]
    assert "PM" in role_ids
    assert "DEV" in role_ids
    assert "QA" in role_ids


# ============================================================
# Test: create_team - Success Path
# ============================================================


def test_create_team_success(template_service, temp_output_dir):
    """create_team should succeed with mocked subprocess."""
    # Mock subprocess.run to succeed
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    # Mock Path.home() to use temp directory
    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            result = template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build a simple app",
            )

    assert result.success is True
    assert result.team_id == "test-project"
    assert "successfully" in result.message.lower()
    assert "test-project" in result.output_dir


def test_create_team_creates_prompts_with_prd_replaced(template_service, temp_output_dir):
    """create_team should replace {prd} in prompt files."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build a TODO app with React",
            )

    # Check PRD was replaced in prompts
    project_dir = Path(temp_output_dir) / "dev" / "tmux-teams" / "test-project"
    pm_prompt = (project_dir / "prompts" / "PM.md").read_text()
    assert "Build a TODO app with React" in pm_prompt
    assert "{prd}" not in pm_prompt


def test_create_team_creates_setup_script(template_service, temp_output_dir):
    """create_team should create executable setup-team.sh."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build an app",
            )

    project_dir = Path(temp_output_dir) / "dev" / "tmux-teams" / "test-project"
    setup_script = project_dir / "setup-team.sh"
    assert setup_script.exists()
    # Check it's executable
    assert os.access(setup_script, os.X_OK)


def test_create_team_creates_all_team_files(template_service, temp_output_dir):
    """create_team should create README, WHITEBOARD, BACKLOG (no PANE_ROLES.md - uses dynamic @role_name)."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build an app",
            )

    # Files are created in docs/tmux/{project_name}/ subdirectory
    team_dir = Path(temp_output_dir) / "dev" / "tmux-teams" / "test-project" / "docs" / "tmux" / "test-project"
    assert (team_dir / "README.md").exists()
    assert (team_dir / "WHITEBOARD.md").exists()
    assert (team_dir / "BACKLOG.md").exists()
    # Note: PANE_ROLES.md removed - uses dynamic @role_name lookup instead


# ============================================================
# Test: create_team - Failure Path
# ============================================================


def test_create_team_failure_missing_template(template_service):
    """create_team should fail for missing template."""
    result = template_service.create_team(
        template_name="nonexistent",
        project_name="test-project",
        prd="Build an app",
    )

    assert result.success is False
    assert "not found" in result.message.lower()


def test_create_team_failure_subprocess_error(template_service, temp_output_dir):
    """create_team should fail when subprocess fails."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "tmux: command not found"

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            result = template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build an app",
            )

    assert result.success is False
    assert "failed" in result.message.lower()
    assert "tmux" in result.message.lower()


def test_create_team_failure_exception(template_service, temp_output_dir):
    """create_team should handle exceptions gracefully."""
    with patch("app.services.template_service.subprocess.run", side_effect=Exception("Boom!")):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            result = template_service.create_team(
                template_name="minimal",
                project_name="test-project",
                prd="Build an app",
            )

    assert result.success is False
    assert "failed" in result.message.lower() or "boom" in result.message.lower()


# ============================================================
# Test: Default Path Resolution (Bug: templates not found)
# ============================================================


def test_default_path_resolves_to_data_templates():
    """TemplateService default path should resolve to PROJECT_ROOT/data/templates/.

    This test verifies the ACTUAL production behavior - not using temp fixtures.
    The service should find templates in the project's data/templates/ directory.
    """
    # Create service with DEFAULT path (no templates_dir argument)
    service = TemplateService()

    # The default path should be PROJECT_ROOT/data/templates/
    # backend/app/services/template_service.py -> project root
    expected_suffix = "data/templates"
    actual_path = str(service.templates_dir)

    assert expected_suffix in actual_path, f"Path should contain '{expected_suffix}', got: {actual_path}"


def test_default_path_lists_actual_templates():
    """TemplateService with default path should list templates from data/templates/.

    This is the ACTUAL bug test - when using default path, list_templates()
    should return the real templates (minimal, standard) from data/templates/.
    """
    # Create service with DEFAULT path (no templates_dir argument)
    service = TemplateService()

    # List templates using default path
    templates = service.list_templates()

    # Should find at least 2 templates (minimal, standard)
    assert len(templates) >= 2, f"Expected at least 2 templates, got {len(templates)}"

    # Verify specific templates exist
    template_names = {t.name for t in templates}
    assert "minimal" in template_names, f"'minimal' template not found. Found: {template_names}"
    assert "standard" in template_names, f"'standard' template not found. Found: {template_names}"


# ============================================================
# Test: create_team with default path (Bug: create broken)
# ============================================================


def test_create_team_with_default_path_finds_template(temp_output_dir):
    """create_team with default path should find templates in data/templates/.

    This tests the ACTUAL bug - create_team() should work when using
    the default templates path (data/templates/).
    """
    # Create service with DEFAULT path (no templates_dir argument)
    service = TemplateService()

    # Mock subprocess to avoid actually running setup-team.sh
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            result = service.create_team(
                template_name="minimal",
                project_name="test-default-path",
                prd="Test PRD content",
            )

    # Should succeed - template found and files created
    assert result.success is True, f"create_team failed: {result.message}"
    assert result.team_id == "test-default-path"
    assert "successfully" in result.message.lower()


def test_create_team_with_default_path_copies_prompts(temp_output_dir):
    """create_team should copy prompts from data/templates/minimal/prompts/.

    Verifies that prompt files are copied and {prd} placeholders are replaced.
    """
    service = TemplateService()

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            service.create_team(
                template_name="minimal",
                project_name="test-prompts",
                prd="MY CUSTOM PRD",
            )

    # Check prompts were copied
    project_dir = Path(temp_output_dir) / "dev" / "tmux-teams" / "test-prompts"
    prompts_dir = project_dir / "prompts"

    assert prompts_dir.exists(), f"prompts/ dir not created at {prompts_dir}"

    # Check PM.md exists and has PRD replaced
    pm_prompt = prompts_dir / "PM.md"
    assert pm_prompt.exists(), "PM.md not copied"

    content = pm_prompt.read_text()
    assert "MY CUSTOM PRD" in content, "PRD not replaced in PM.md"
    assert "{prd}" not in content, "{prd} placeholder not replaced"


def test_create_team_error_includes_stdout_when_stderr_empty(template_service, temp_output_dir):
    """When setup script fails with empty stderr, error should include stdout.

    This is the BUG: Script outputs to stdout but error message only shows stderr.
    When stderr is empty, the error message gives no useful information.
    """
    # Mock subprocess to fail with non-zero code, empty stderr but info in stdout
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = "Starting setup...\nWaiting for Claude Code...\nTimeout waiting for pane 0"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            result = template_service.create_team(
                template_name="minimal",
                project_name="test-error-output",
                prd="Test PRD",
            )

    assert result.success is False
    # BUG: Currently only shows stderr (empty), should include stdout
    assert "Timeout" in result.message or "stdout" in result.message.lower(), \
        f"Error should include stdout info when stderr empty. Got: {result.message}"


def test_setup_script_starts_claude_and_init_role(template_service, temp_output_dir):
    """Generated setup-team.sh should start Claude Code and run /init-role.

    The script must:
    1. Create tmux session with panes
    2. Start Claude Code in each pane
    3. Run /init-role for each role
    """
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Setup complete!"
    mock_result.stderr = ""

    with patch("app.services.template_service.subprocess.run", return_value=mock_result):
        with patch("app.services.template_service.Path.home", return_value=Path(temp_output_dir)):
            template_service.create_team(
                template_name="minimal",
                project_name="test-claude-init",
                prd="Test PRD",
            )

    # Read generated setup script
    project_dir = Path(temp_output_dir) / "dev" / "tmux-teams" / "test-claude-init"
    setup_script = project_dir / "setup-team.sh"
    assert setup_script.exists(), "setup-team.sh not created"

    script_content = setup_script.read_text()

    # Must start Claude Code in panes
    assert "claude" in script_content, "Script must start Claude Code"
    assert "send-keys" in script_content, "Script must use send-keys to start Claude"

    # Must run /init-role for each role
    assert "/init-role" in script_content, "Script must run /init-role"
    assert "PM" in script_content, "Script must init PM role"
    assert "CODER" in script_content, "Script must init CODER role"
