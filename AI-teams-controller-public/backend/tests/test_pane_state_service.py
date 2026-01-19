# -*- coding: utf-8 -*-
"""Tests for PaneStateService (Sprint 6 - SRP extraction).

PaneStateService handles pane state operations (get_pane_state, send_message)
extracted from TmuxService to follow Single Responsibility Principle.
"""

from unittest.mock import patch, MagicMock
import pytest

from app.services.pane_state_service import PaneStateService


class TestPaneStateService:
    """Test PaneStateService initialization and basic operations."""

    @pytest.fixture
    def service(self):
        """Create PaneStateService instance for testing."""
        return PaneStateService(capture_lines=100)

    def test_initialization(self, service):
        """Should initialize with capture_lines."""
        assert service.capture_lines == 100

    def test_custom_capture_lines(self):
        """Should accept custom capture_lines."""
        service = PaneStateService(capture_lines=200)
        assert service.capture_lines == 200


class TestGetPaneState:
    """Test get_pane_state method."""

    @pytest.fixture
    def service(self):
        return PaneStateService(capture_lines=100)

    def test_get_pane_state_success(self, service):
        """Should capture pane content and return state."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            # Mock: capture-pane returns content
            mock_run.return_value = (True, "pane content line 1\nline 2")

            with patch.object(service, '_get_pane_index', return_value="0"):
                with patch.object(service._activity_detector, 'get_pane_activity', return_value=True):
                    result = service.get_pane_state("test-team", "pane-0")

                    assert "pane content" in result["output"]
                    assert result["isActive"] is True
                    assert "lastUpdated" in result
                    assert "highlightText" in result

    def test_get_pane_state_pane_not_found(self, service):
        """Should return error when pane not found."""
        with patch.object(service, '_get_pane_index', return_value=None):
            result = service.get_pane_state("test-team", "invalid-pane")

            assert "not found" in result["output"].lower()
            assert result["isActive"] is False

    def test_get_pane_state_capture_failure(self, service):
        """Should handle capture failure gracefully."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            mock_run.return_value = (False, "capture failed")

            with patch.object(service, '_get_pane_index', return_value="0"):
                result = service.get_pane_state("test-team", "pane-0")

                assert "failed" in result["output"].lower()

    def test_get_pane_state_uses_escape_flag(self, service):
        """Should use -e flag to preserve ANSI sequences."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            mock_run.return_value = (True, "test output")

            with patch.object(service, '_get_pane_index', return_value="0"):
                service.get_pane_state("test-team", "pane-0")

                # Verify capture-pane was called with -e flag
                call_args = mock_run.call_args[0][0]
                assert "capture-pane" in call_args
                assert "-e" in call_args


class TestSendMessage:
    """Test send_message method."""

    @pytest.fixture
    def service(self):
        return PaneStateService(capture_lines=100)

    def test_send_message_success(self, service):
        """Should send message with two-enter rule."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            mock_run.return_value = (True, "")

            with patch.object(service, '_get_pane_index', return_value="0"):
                result = service.send_message("test-team", "pane-0", "test message")

                assert result["success"] is True
                # Should call run 3 times: send-keys, Enter, Enter
                assert mock_run.call_count == 3

    def test_send_message_pane_not_found(self, service):
        """Should return error if pane not found."""
        with patch.object(service, '_get_pane_index', return_value=None):
            result = service.send_message("test-team", "invalid-pane", "test")

            assert result["success"] is False
            assert "not found" in result["message"].lower()

    def test_send_message_escape_key(self, service):
        """Should handle Escape key specially."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            mock_run.return_value = (True, "")

            with patch.object(service, '_get_pane_index', return_value="0"):
                result = service.send_message("test-team", "pane-0", "\x1b")

                assert result["success"] is True
                # Verify Escape was sent (not Enter)
                call_args = mock_run.call_args[0][0]
                assert "Escape" in call_args

    def test_send_message_tracks_for_highlight(self, service):
        """Should track sent message for highlighting."""
        with patch('app.services.pane_state_service.TmuxRunner.run') as mock_run:
            mock_run.return_value = (True, "")

            with patch.object(service, '_get_pane_index', return_value="0"):
                service.send_message("test-team", "pane-0", "test message")

                # Get pane state should include highlight
                with patch.object(service._activity_detector, 'get_pane_activity', return_value=False):
                    result = service.get_pane_state("test-team", "pane-0")

                    assert result["highlightText"] is not None
                    assert "test message" in result["highlightText"]


class TestSetCaptureLines:
    """Test set_capture_lines method."""

    def test_set_capture_lines_updates_attribute(self):
        """Should update capture_lines attribute."""
        service = PaneStateService(capture_lines=100)
        service.set_capture_lines(200)
        assert service.capture_lines == 200
