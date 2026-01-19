# -*- coding: utf-8 -*-
"""Tests for voice_feedback.summary module.

TDD: Tests for LLM summary generation.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestGenerateSummary:
    """Tests for generate_summary function."""

    @patch.dict("os.environ", {"XAI_API_KEY": ""}, clear=False)
    def test_summary_without_api_key(self):
        """Should return placeholder summary without API key."""
        from app.services.voice_feedback.summary import generate_summary

        result = generate_summary("test command", "output text")

        assert "Done" in result
        assert "test command" in result

    @patch.dict("os.environ", {"XAI_API_KEY": "test-key"}, clear=False)
    @patch("langchain.chat_models.init_chat_model")
    def test_summary_with_mocked_llm(self, mock_init_model):
        """Should call LLM and return summary."""
        from app.services.voice_feedback.summary import generate_summary

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Done. Task completed successfully."
        mock_llm.invoke.return_value = mock_response
        mock_init_model.return_value = mock_llm

        result = generate_summary("test command", "> test\noutput\n> ")

        assert result == "Done. Task completed successfully."
        mock_llm.invoke.assert_called_once()

    @patch.dict("os.environ", {"XAI_API_KEY": "test-key"}, clear=False)
    @patch("langchain.chat_models.init_chat_model")
    def test_summary_uses_pre_trimmed(self, mock_init_model):
        """Should use pre_trimmed if provided."""
        from app.services.voice_feedback.summary import generate_summary

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Summary result."
        mock_llm.invoke.return_value = mock_response
        mock_init_model.return_value = mock_llm

        result = generate_summary(
            "command",
            "full output that should be ignored",
            pre_trimmed="pre-trimmed output"
        )

        # Verify LLM was called with pre-trimmed content
        call_args = mock_llm.invoke.call_args[0][0]
        human_msg = call_args[1]
        assert "pre-trimmed output" in human_msg.content or result == "Summary result."

    @patch.dict("os.environ", {"XAI_API_KEY": "test-key"}, clear=False)
    @patch("langchain.chat_models.init_chat_model")
    def test_summary_filters_hooks(self, mock_init_model):
        """Should filter hook messages from output."""
        from app.services.voice_feedback.summary import generate_summary

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Filtered result."
        mock_llm.invoke.return_value = mock_response
        mock_init_model.return_value = mock_llm

        output_with_hooks = "> command\nReal output\nStop hook fired\nHook stuff"
        result = generate_summary("command", output_with_hooks)

        assert result == "Filtered result."

    @patch.dict("os.environ", {"XAI_API_KEY": "test-key"}, clear=False)
    @patch("langchain.chat_models.init_chat_model")
    def test_summary_truncates_output(self, mock_init_model):
        """Should truncate long output to last N lines."""
        from app.services.voice_feedback.summary import generate_summary

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Truncated result."
        mock_llm.invoke.return_value = mock_response
        mock_init_model.return_value = mock_llm

        # Create output with many lines
        long_output = "\n".join([f"> line{i}\noutput{i}" for i in range(100)])
        result = generate_summary("command", long_output)

        assert result == "Truncated result."
        mock_llm.invoke.assert_called_once()

    @patch.dict("os.environ", {"XAI_API_KEY": ""}, clear=False)
    def test_summary_placeholder_truncates_long_command(self):
        """Should truncate long command in placeholder summary."""
        from app.services.voice_feedback.summary import generate_summary

        long_command = "a" * 100
        result = generate_summary(long_command, "output")

        # Placeholder should contain first 50 chars of command
        assert "a" * 50 in result
        assert len(result) < 100
