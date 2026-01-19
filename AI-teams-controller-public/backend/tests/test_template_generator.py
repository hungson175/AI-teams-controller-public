# -*- coding: utf-8 -*-
"""Tests for TemplateGenerator extraction from template_service.py.

This test file is part of Sprint R1 TDD refactoring.
Tests are written BEFORE extracting TemplateGenerator class to ensure
the new structure maintains existing functionality.

TemplateGenerator should handle:
- README generation
- WHITEBOARD generation
- BACKLOG generation
- Setup script generation
- Init role skill generation
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


class TestTemplateGeneratorModule:
    """Verify TemplateGenerator class structure after extraction."""

    def test_template_generator_class_exists(self):
        """TemplateGenerator class should be importable after extraction."""
        # Class should now exist after extraction
        from app.services.template_generator import TemplateGenerator
        assert TemplateGenerator is not None

    def test_template_generator_has_required_methods(self):
        """TemplateGenerator should have all generation methods."""
        from app.services.template_generator import TemplateGenerator

        generator = TemplateGenerator()
        # Verify all methods exist
        assert hasattr(generator, "generate_readme")
        assert hasattr(generator, "generate_whiteboard")
        assert hasattr(generator, "generate_backlog")
        assert hasattr(generator, "generate_setup_script")
        assert hasattr(generator, "generate_init_role_skill")


class TestReadmeGeneration:
    """Test README generation logic."""

    def test_generate_readme_creates_file(self):
        """Should create README.md with project details."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        project_name = "Test Team"
        template = TeamTemplate(
            name="test-template",
            display_name="Test Template",
            description="Test",
            version="1.0.0",
            roles=[TemplateRole(id="PO", name="Product Owner", description="Test role", pane_index=0)]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_readme(output_dir, project_name, template)

            # Verify README was written
            mock_write.assert_called_once()
            content = mock_write.call_args[0][0]
            assert "# Test Team" in content
            assert "Test Template" in content

    def test_generate_readme_content_structure(self):
        """README should have proper markdown structure."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[TemplateRole(id="PM", name="Project Manager", description="Test", pane_index=0)]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_readme(output_dir, "MyProject", template)

            content = mock_write.call_args[0][0]
            # Should have header
            assert content.startswith("# ")
            # Should have sections
            assert "## " in content


class TestWhiteboardGeneration:
    """Test WHITEBOARD generation logic."""

    def test_generate_whiteboard_creates_file(self):
        """Should create WHITEBOARD.md."""
        from app.services.template_generator import TemplateGenerator

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_whiteboard(output_dir, "TestProject")

            # Verify file was written
            mock_write.assert_called_once()
            content = mock_write.call_args[0][0]
            assert "WHITEBOARD" in content or "whiteboard" in content.lower()

    def test_generate_whiteboard_has_team_status(self):
        """WHITEBOARD should include team status table."""
        from app.services.template_generator import TemplateGenerator

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_whiteboard(output_dir, "TestProject")

            content = mock_write.call_args[0][0]
            # Should have markdown table structure
            assert "|" in content


class TestBacklogGeneration:
    """Test BACKLOG generation logic."""

    def test_generate_backlog_creates_file(self):
        """Should create BACKLOG.md."""
        from app.services.template_generator import TemplateGenerator

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_backlog(output_dir, "TestProject")

            # Verify file was written
            mock_write.assert_called_once()
            content = mock_write.call_args[0][0]
            assert "BACKLOG" in content or "backlog" in content.lower()

    def test_generate_backlog_has_priority_sections(self):
        """BACKLOG should have priority sections."""
        from app.services.template_generator import TemplateGenerator

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_backlog(output_dir, "TestProject")

            content = mock_write.call_args[0][0]
            # Should have headers for different priorities
            assert "##" in content


class TestSetupScriptGeneration:
    """Test setup script generation logic."""

    def test_generate_setup_script_creates_file(self):
        """Should create setup-team.sh script."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[
                TemplateRole(id="PO", name="Product Owner", description="Test", pane_index=0),
                TemplateRole(id="SM", name="Scrum Master", description="Test", pane_index=1),
            ]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write, \
             patch("pathlib.Path.chmod"):
            generator.generate_setup_script(output_dir, "test-team", template)

            # Verify script was written
            mock_write.assert_called_once()
            content = mock_write.call_args[0][0]
            assert "#!/bin/bash" in content

    def test_generate_setup_script_has_role_setup(self):
        """Setup script should configure each role."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[
                TemplateRole(id="PO", name="Product Owner", description="Test", pane_index=0),
                TemplateRole(id="BE", name="Backend", description="Test", pane_index=4),
            ]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write, \
             patch("pathlib.Path.chmod"):
            generator.generate_setup_script(output_dir, "test-team", template)

            content = mock_write.call_args[0][0]
            # Should reference both roles
            assert "PO" in content
            assert "BE" in content

    def test_generate_setup_script_is_executable(self):
        """Setup script should be made executable."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[TemplateRole(id="PO", name="Product Owner", description="Test", pane_index=0)]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text"), \
             patch("pathlib.Path.chmod") as mock_chmod:
            generator.generate_setup_script(output_dir, "test-team", template)

            # Should call chmod to make executable
            mock_chmod.assert_called_once()


class TestInitRoleSkillGeneration:
    """Test init-role skill generation logic."""

    def test_generate_init_role_skill_creates_file(self):
        """Should create init-role.skill file."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        team_name = "test-team"
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[TemplateRole(id="PO", name="Product Owner", description="Test", pane_index=0)]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_init_role_skill(output_dir, team_name, template)

            # Verify skill file was written
            mock_write.assert_called_once()
            content = mock_write.call_args[0][0]
            # Should contain skill content
            assert len(content) > 0

    def test_generate_init_role_skill_references_team(self):
        """Init role skill should reference the team name."""
        from app.services.template_generator import TemplateGenerator
        from app.models.schemas import TeamTemplate, TemplateRole

        generator = TemplateGenerator()
        output_dir = Path("/tmp/test-team")
        team_name = "my-awesome-team"
        template = TeamTemplate(
            name="test",
            display_name="Test",
            description="Test",
            version="1.0.0",
            roles=[TemplateRole(id="PO", name="Product Owner", description="Test", pane_index=0)]
        )

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text") as mock_write:
            generator.generate_init_role_skill(output_dir, team_name, template)

            content = mock_write.call_args[0][0]
            # Should mention the team name
            assert team_name in content


class TestTemplateGeneratorIntegration:
    """Test TemplateGenerator integration with TemplateService."""

    def test_template_service_uses_generator(self):
        """After extraction, TemplateService should use TemplateGenerator."""
        from app.services.template_service import TemplateService

        service = TemplateService()
        # Verify service has generator instance
        assert hasattr(service, "generator")
        assert service.generator is not None

    def test_all_generation_methods_accessible(self):
        """All generation methods should be accessible via generator."""
        from app.services.template_service import TemplateService

        service = TemplateService()

        # After extraction - methods should be on generator, not service
        assert hasattr(service.generator, "generate_readme")
        assert hasattr(service.generator, "generate_whiteboard")
        assert hasattr(service.generator, "generate_backlog")
        assert hasattr(service.generator, "generate_setup_script")
        assert hasattr(service.generator, "generate_init_role_skill")
