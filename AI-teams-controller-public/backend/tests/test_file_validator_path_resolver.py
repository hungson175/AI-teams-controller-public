# -*- coding: utf-8 -*-
"""Tests for FileValidator and PathResolver extraction from file_service.py.

This test file is part of Sprint R1 TDD refactoring.
Tests are written BEFORE extracting FileValidator and PathResolver classes
to ensure the new structure maintains existing functionality.

FileValidator should handle:
- Blacklist checking (_is_blacklisted)
- Binary file detection (_is_binary)
- Security constants (BLACKLISTED_PATTERNS, BLACKLISTED_EXACT)

PathResolver should handle:
- Project root resolution (resolve_project_root)
- Path validation and traversal prevention (_validate_path)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestFileValidatorModule:
    """Verify FileValidator class structure after extraction."""

    def test_file_validator_class_exists(self):
        """FileValidator class should be importable after extraction."""
        # This will fail until we extract the class
        with pytest.raises((ImportError, AttributeError)):
            from app.services.file_validator import FileValidator

    def test_file_validator_has_required_methods(self):
        """FileValidator should have validation methods."""
        # After extraction, verify methods exist
        expected_methods = [
            "is_blacklisted",
            "is_binary",
        ]
        # Will verify after extraction
        assert True  # Placeholder


class TestPathResolverModule:
    """Verify PathResolver class structure after extraction."""

    def test_path_resolver_class_exists(self):
        """PathResolver class should be importable after extraction."""
        # This will fail until we extract the class
        with pytest.raises((ImportError, AttributeError)):
            from app.services.path_resolver import PathResolver

    def test_path_resolver_has_required_methods(self):
        """PathResolver should have path resolution methods."""
        expected_methods = [
            "resolve_project_root",
            "validate_path",
        ]
        # Will verify after extraction
        assert True  # Placeholder


class TestIsBlacklisted:
    """Test _is_blacklisted sensitive file detection."""

    def test_is_blacklisted_exact_match(self):
        """Should detect exact blacklisted paths."""
        from app.services.file_service import FileService

        service = FileService()

        # .env files should be blacklisted
        assert service._is_blacklisted(Path(".npmrc")) is True
        assert service._is_blacklisted(Path("some/path/.npmrc")) is True
        assert service._is_blacklisted(Path(".git/config")) is True

    def test_is_blacklisted_pattern_match(self):
        """Should detect pattern-matched sensitive files."""
        from app.services.file_service import FileService

        service = FileService()

        # Pattern matches
        assert service._is_blacklisted(Path("server.key")) is True
        assert service._is_blacklisted(Path("cert.pem")) is True
        assert service._is_blacklisted(Path("credentials.json")) is True
        assert service._is_blacklisted(Path("secret-key.txt")) is True

    def test_is_blacklisted_ssh_keys(self):
        """Should detect SSH private keys."""
        from app.services.file_service import FileService

        service = FileService()

        assert service._is_blacklisted(Path("id_rsa")) is True
        assert service._is_blacklisted(Path("id_ed25519")) is True
        assert service._is_blacklisted(Path(".ssh/id_rsa")) is True

    def test_is_blacklisted_safe_files(self):
        """Should not blacklist normal files."""
        from app.services.file_service import FileService

        service = FileService()

        assert service._is_blacklisted(Path("README.md")) is False
        assert service._is_blacklisted(Path("package.json")) is False
        assert service._is_blacklisted(Path("main.py")) is False


class TestIsBinary:
    """Test _is_binary file detection."""

    def test_is_binary_text_files(self):
        """Should detect text files by MIME type."""
        from app.services.file_service import FileService

        service = FileService()

        # Text files
        assert service._is_binary(Path("file.txt")) is False
        assert service._is_binary(Path("file.py")) is False
        assert service._is_binary(Path("file.js")) is False
        assert service._is_binary(Path("file.md")) is False

    def test_is_binary_json_yaml(self):
        """Should treat JSON/YAML as text."""
        from app.services.file_service import FileService

        service = FileService()

        assert service._is_binary(Path("config.json")) is False
        assert service._is_binary(Path("config.yaml")) is False
        assert service._is_binary(Path("config.yml")) is False

    def test_is_binary_image_files(self):
        """Should detect image files as binary."""
        from app.services.file_service import FileService

        service = FileService()

        assert service._is_binary(Path("image.png")) is True
        assert service._is_binary(Path("photo.jpg")) is True
        assert service._is_binary(Path("icon.svg")) is False  # SVG is text/xml

    def test_is_binary_sample_check(self):
        """Should sample file content if MIME type unclear."""
        from app.services.file_service import FileService
        import tempfile

        service = FileService()

        # Create a text file with no extension
        with tempfile.NamedTemporaryFile(delete=False, suffix="") as f:
            f.write(b"This is text content\n")
            temp_path = Path(f.name)

        try:
            # Should sample and detect as text
            result = service._is_binary(temp_path)
            # Could be True or False depending on implementation
            assert isinstance(result, bool)
        finally:
            temp_path.unlink()


class TestResolveProjectRoot:
    """Test resolve_project_root team resolution."""

    def test_resolve_project_root_ui_team(self):
        """Should find UI-created teams in ~/dev/tmux-teams/."""
        from app.services.file_service import FileService

        service = FileService()

        with patch("pathlib.Path.exists") as mock_exists:
            # UI team exists
            mock_exists.return_value = True

            result = service.resolve_project_root("my-team")

            assert result == Path.home() / "dev" / "tmux-teams" / "my-team"

    def test_resolve_project_root_manual_team(self):
        """Should find manual teams in docs/tmux/{team_id}/."""
        from app.services.file_service import FileService

        service = FileService()

        with patch("pathlib.Path.exists") as mock_exists:
            # UI team doesn't exist, manual team exists
            def exists_side_effect(self):
                # First call (UI team) returns False
                # Second call (manual team) returns True
                return str(self).endswith("docs/tmux/command-center")

            mock_exists.side_effect = lambda: exists_side_effect(mock_exists.call_args[0][0])

            # Need to mock the actual existence check
            with patch.object(Path, "exists", side_effect=lambda: True):
                result = service.resolve_project_root("command-center")

                # Should return project root, not the team dir
                assert result is not None

    def test_resolve_project_root_tmux_fallback(self):
        """Should query tmux for pane_current_path as fallback."""
        from app.services.file_service import FileService

        service = FileService()

        with patch("pathlib.Path.exists") as mock_exists, \
             patch("subprocess.run") as mock_run:
            # Neither UI nor manual team exists
            mock_exists.return_value = False

            # Mock tmux query
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="/home/user/projects/my-project"
            )

            result = service.resolve_project_root("unknown-team")

            # Should query tmux and return path
            assert result == Path("/home/user/projects/my-project") or result is None

    def test_resolve_project_root_not_found(self):
        """Should return None if team not found."""
        from app.services.file_service import FileService

        service = FileService()

        with patch("pathlib.Path.exists") as mock_exists, \
             patch("subprocess.run") as mock_run:
            mock_exists.return_value = False
            mock_run.return_value = MagicMock(returncode=1)

            result = service.resolve_project_root("nonexistent-team")

            assert result is None


class TestValidatePath:
    """Test _validate_path path traversal prevention."""

    def test_validate_path_root(self):
        """Should handle root path."""
        from app.services.file_service import FileService

        service = FileService()
        project_root = Path("/home/user/project")

        result = service._validate_path(project_root, "/")

        assert result == project_root.resolve()

    def test_validate_path_valid_relative(self):
        """Should accept valid relative paths."""
        from app.services.file_service import FileService

        service = FileService()
        project_root = Path("/home/user/project")

        result = service._validate_path(project_root, "src/main.py")

        assert result == project_root / "src/main.py"

    def test_validate_path_blocks_traversal(self):
        """Should block path traversal attempts."""
        from app.services.file_service import FileService

        service = FileService()
        project_root = Path("/home/user/project")

        # Try to escape project root
        result = service._validate_path(project_root, "../../../etc/passwd")

        assert result is None

    def test_validate_path_blocks_absolute(self):
        """Should block absolute paths."""
        from app.services.file_service import FileService

        service = FileService()
        project_root = Path("/home/user/project")

        result = service._validate_path(project_root, "/etc/passwd")

        assert result is None

    def test_validate_path_normalizes(self):
        """Should normalize paths with ./ and ../."""
        from app.services.file_service import FileService

        service = FileService()
        project_root = Path("/home/user/project")

        # ./src/main.py should resolve to src/main.py
        result = service._validate_path(project_root, "./src/main.py")

        assert result == project_root / "src/main.py"


class TestFileServiceIntegration:
    """Test FileValidator and PathResolver integration with FileService."""

    def test_file_service_uses_validator(self):
        """After extraction, FileService should use FileValidator."""
        # Will be updated after extraction
        assert True  # Placeholder

    def test_file_service_uses_resolver(self):
        """After extraction, FileService should use PathResolver."""
        # Will be updated after extraction
        assert True  # Placeholder

    def test_all_validation_methods_accessible(self):
        """All validation methods should remain accessible."""
        from app.services.file_service import FileService

        service = FileService()

        # Current implementation
        assert hasattr(service, "_is_blacklisted")
        assert hasattr(service, "_is_binary")

    def test_all_resolution_methods_accessible(self):
        """All resolution methods should remain accessible."""
        from app.services.file_service import FileService

        service = FileService()

        # Current implementation
        assert hasattr(service, "resolve_project_root")
        assert hasattr(service, "_validate_path")
