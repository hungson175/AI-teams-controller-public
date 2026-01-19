# -*- coding: utf-8 -*-
"""Tests for Celery voice feedback tasks.

All external dependencies (LLM, TTS, Redis) are mocked.
"""

import base64
from unittest.mock import patch, MagicMock

import pytest


class TestGenerateSummary:
    """Test _generate_summary function."""

    def test_summary_without_api_key(self):
        """Should return placeholder when XAI_API_KEY not set."""
        with patch.dict("os.environ", {"XAI_API_KEY": ""}, clear=False):
            from app.services.celery_tasks import _generate_summary

            result = _generate_summary("fix bug", "pane output")

            assert "Done" in result or "Completed" in result
            assert "fix bug" in result

    def test_summary_with_mocked_llm(self, mock_llm):
        """Should call LLM and return summary."""
        with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            with patch(
                "langchain.chat_models.init_chat_model",
                return_value=mock_llm
            ):
                from app.services.celery_tasks import _generate_summary

                result = _generate_summary("fix bug", "pane output\nDone.")

                assert result == "Done. Task completed successfully."
                mock_llm.invoke.assert_called_once()

    def test_summary_truncates_output(self, mock_llm):
        """Should only use last 100 lines of pane output (increased from 50 for narrow pane support)."""
        with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            with patch(
                "langchain.chat_models.init_chat_model",
                return_value=mock_llm
            ):
                from app.services.celery_tasks import _generate_summary

                # Create 150 lines of output
                long_output = "\n".join([f"line {i}" for i in range(150)])
                _generate_summary("command", long_output)

                # Check that invoke was called
                call_args = mock_llm.invoke.call_args
                messages = call_args[0][0]
                human_msg = messages[1].content

                # Should contain line 149 (last line) but not line 0
                assert "line 149" in human_msg
                # First 50 lines should be truncated (only last 100 included)
                assert "line 0\n" not in human_msg
                assert "line 49\n" not in human_msg


class TestGenerateTTS:
    """Test _generate_tts function."""

    def test_tts_without_provider(self):
        """Should return empty string when TTSProviderFactory.create() fails."""
        with patch(
            "app.services.tts_providers.TTSProviderFactory.create",
            side_effect=ValueError("No TTS provider configured")
        ):
            from app.services.celery_tasks import _generate_tts

            result = _generate_tts("Test summary")

            assert result == ""

    def test_tts_with_mocked_provider(self):
        """Should call TTSProviderFactory and return base64 audio."""
        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = base64.b64encode(b"fake_audio_bytes").decode()

        with patch(
            "app.services.tts_providers.TTSProviderFactory.create",
            return_value=mock_provider
        ):
            from app.services.celery_tasks import _generate_tts

            result = _generate_tts("Test summary")

            # Should be base64 encoded
            assert result == base64.b64encode(b"fake_audio_bytes").decode()
            mock_provider.generate_speech_base64.assert_called_once_with("Test summary")


class TestBroadcastFeedback:
    """Test _broadcast_feedback function."""

    def test_broadcast_publishes_to_redis(self, mock_redis_client):
        """Should publish message to Redis channel."""
        with patch(
            "app.services.voice_feedback.broadcast.get_redis_client",
            return_value=mock_redis_client
        ):
            from app.services.celery_tasks import _broadcast_feedback

            _broadcast_feedback(
                team_id="team1",
                role_id="pane-0",
                summary="Done.",
                audio="base64audio",
            )

            mock_redis_client.publish.assert_called_once()
            call_args = mock_redis_client.publish.call_args
            channel = call_args[0][0]
            message = call_args[0][1]

            assert channel == "voice_feedback"
            assert "team1" in message
            assert "pane-0" in message
            assert "Done." in message

    def test_broadcast_includes_timestamp(self, mock_redis_client):
        """Should include timestamp in message."""
        import json

        with patch(
            "app.services.voice_feedback.broadcast.get_redis_client",
            return_value=mock_redis_client
        ):
            from app.services.celery_tasks import _broadcast_feedback

            _broadcast_feedback(
                team_id="team1",
                role_id="pane-0",
                summary="Done.",
                audio="",
            )

            call_args = mock_redis_client.publish.call_args
            message_str = call_args[0][1]
            message = json.loads(message_str)

            assert "timestamp" in message
            assert isinstance(message["timestamp"], int)

    def test_broadcast_redis_failure(self, mock_redis_client):
        """Should raise on Redis publish failure."""
        mock_redis_client.publish.side_effect = Exception("Redis error")

        with patch(
            "app.services.voice_feedback.broadcast.get_redis_client",
            return_value=mock_redis_client
        ):
            from app.services.celery_tasks import _broadcast_feedback

            with pytest.raises(Exception, match="Redis error"):
                _broadcast_feedback("team", "pane", "summary", "audio")


class TestProcessVoiceFeedback:
    """Test process_voice_feedback Celery task."""

    def test_full_flow_success(self, mock_llm, mock_redis_client):
        """Should process full flow: summary -> TTS -> broadcast."""
        # Create mock TTS provider
        mock_tts_provider = MagicMock()
        mock_tts_provider.generate_speech_base64.return_value = base64.b64encode(b"fake_audio").decode()

        with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            with patch(
                "langchain.chat_models.init_chat_model",
                return_value=mock_llm
            ):
                with patch(
                    "app.services.tts_providers.TTSProviderFactory.create",
                    return_value=mock_tts_provider
                ):
                    with patch(
                        "app.services.voice_feedback.broadcast.get_redis_client",
                        return_value=mock_redis_client
                    ):
                        with patch(
                            "app.services.voice_feedback.content.get_redis_client",
                            return_value=mock_redis_client
                        ):
                            from app.services.celery_tasks import process_voice_feedback

                            # Call directly using .run() to bypass Celery task wrapper
                            result = process_voice_feedback.run(
                                team_id="team1",
                                role_id="pane-0",
                                pane_output="Task done.\n",
                                original_command="fix bug",
                            )

                            assert result["success"] is True
                            assert result["team_id"] == "team1"
                            assert result["role_id"] == "pane-0"
                            assert "summary" in result

                            # Verify all steps were called
                            mock_llm.invoke.assert_called_once()

                            # Sprint 40: TTS called TWICE (summary + team name)
                            assert mock_tts_provider.generate_speech_base64.call_count == 2
                            # First call: summary TTS
                            first_call = mock_tts_provider.generate_speech_base64.call_args_list[0]
                            assert first_call[0][0] == "Done. Task completed successfully."
                            # Second call: team name TTS (formatted)
                            second_call = mock_tts_provider.generate_speech_base64.call_args_list[1]
                            assert second_call[0][0] == "team1"  # "team1" has no underscores/hyphens

                            mock_redis_client.publish.assert_called_once()

    def test_flow_with_llm_failure(self, mock_redis_client):
        """Should handle LLM failure gracefully."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM API error")

        # Mock Redis to return no duplicate (new content)
        mock_redis_client.get.return_value = None

        with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            with patch(
                "app.services.voice_feedback.content.get_redis_client",
                return_value=mock_redis_client
            ):
                with patch(
                    "langchain.chat_models.init_chat_model",
                    return_value=mock_llm
                ):
                    from app.services.celery_tasks import process_voice_feedback

                    result = process_voice_feedback.run(
                        team_id="team1",
                        role_id="pane-0",
                        pane_output="> cmd\noutput\n> current",  # Need prompts for trim
                        original_command="cmd",
                    )

                    assert result["success"] is False
                    assert "error" in result

    def test_flow_without_api_keys(self, mock_redis_client):
        """Should use placeholders without API keys."""
        with patch.dict("os.environ", {
            "XAI_API_KEY": "",
            "OPENAI_API_KEY": "",
        }, clear=False):
            with patch(
                "app.services.voice_feedback.content.get_redis_client",
                return_value=mock_redis_client
            ):
                with patch(
                    "app.services.voice_feedback.broadcast.get_redis_client",
                    return_value=mock_redis_client
                ):
                    from app.services.celery_tasks import process_voice_feedback

                    result = process_voice_feedback.run(
                        team_id="team1",
                        role_id="pane-0",
                        pane_output="output",
                        original_command="fix bug",
                    )

                    # Should still succeed with placeholders
                    assert result["success"] is True
                    # Summary should contain command
                    assert "fix bug" in result["summary"]


class TestFormatTeamName:
    """Test format_team_name function."""

    def test_format_underscores(self):
        """Should replace underscores with spaces."""
        from app.services.celery_tasks import format_team_name

        result = format_team_name("ai_controller_full_team")
        assert result == "ai controller full team"

    def test_format_hyphens(self):
        """Should replace hyphens with spaces."""
        from app.services.celery_tasks import format_team_name

        result = format_team_name("project-foo-bar")
        assert result == "project foo bar"

    def test_format_simple_name(self):
        """Should return simple names unchanged."""
        from app.services.celery_tasks import format_team_name

        result = format_team_name("simple")
        assert result == "simple"

    def test_format_mixed_separators(self):
        """Should handle both underscores and hyphens."""
        from app.services.celery_tasks import format_team_name

        result = format_team_name("my_project-team")
        assert result == "my project team"

    def test_format_empty_string(self):
        """Should handle empty string."""
        from app.services.celery_tasks import format_team_name

        result = format_team_name("")
        assert result == ""


class TestTrimToLastInput:
    """Test _trim_to_last_input function."""

    def test_trim_with_multiple_prompts(self):
        """Should trim to second-to-last prompt (last user input)."""
        from app.services.celery_tasks import _trim_to_last_input

        pane_output = """old stuff line 1
old stuff line 2
> first command
first output line 1
first output line 2
> second command
second output line 1
second output line 2
> (current prompt)"""

        result = _trim_to_last_input(pane_output)

        # Should start from "second command" (second-to-last >)
        assert "> second command" in result
        assert "second output line 1" in result
        assert "second output line 2" in result
        assert "> (current prompt)" in result
        # Should NOT include old content or first command
        assert "old stuff" not in result
        assert "first command" not in result
        assert "first output" not in result

    def test_trim_with_exactly_two_prompts(self):
        """Should work with exactly 2 prompts (minimum case)."""
        from app.services.celery_tasks import _trim_to_last_input

        pane_output = """> only command
output from command
> current prompt"""

        result = _trim_to_last_input(pane_output)

        # Should keep everything (second-to-last is the first one)
        assert "> only command" in result
        assert "output from command" in result
        assert "> current prompt" in result

    def test_trim_with_single_prompt(self):
        """Should return full output when less than 2 prompts."""
        from app.services.celery_tasks import _trim_to_last_input

        pane_output = """some output
> single prompt"""

        result = _trim_to_last_input(pane_output)

        # Should return original (can't trim)
        assert result == pane_output

    def test_trim_with_no_prompts(self):
        """Should return full output when no prompts found."""
        from app.services.celery_tasks import _trim_to_last_input

        pane_output = """just some text
without any prompts"""

        result = _trim_to_last_input(pane_output)

        # Should return original (can't trim)
        assert result == pane_output

    def test_trim_with_indented_prompts(self):
        """Should detect prompts even with leading whitespace."""
        from app.services.celery_tasks import _trim_to_last_input

        pane_output = """old stuff
  > first input
output
  > second input
more output
  > current"""

        result = _trim_to_last_input(pane_output)

        # Should trim to second-to-last (note: whitespace-stripped comparison)
        assert "second input" in result
        assert "more output" in result
        assert "first input" not in result

    def test_trim_empty_string(self):
        """Should handle empty string."""
        from app.services.celery_tasks import _trim_to_last_input

        result = _trim_to_last_input("")

        assert result == ""

    def test_trim_reduces_line_count(self):
        """Should significantly reduce line count for large outputs."""
        from app.services.celery_tasks import _trim_to_last_input

        # Simulate 200 lines of old content
        old_lines = [f"old line {i}" for i in range(200)]
        recent_lines = [
            "> recent command",
            "recent output line 1",
            "recent output line 2",
            "> current prompt"
        ]
        pane_output = "\n".join(old_lines + recent_lines)

        result = _trim_to_last_input(pane_output)
        result_lines = result.split("\n")

        # Should have only 4 lines (the recent ones)
        assert len(result_lines) == 4
        assert result_lines[0] == "> recent command"


class TestGetRedisClient:
    """Test get_redis_client function."""

    def test_returns_redis_client(self):
        """Should return a Redis client instance."""
        with patch("app.services.voice_feedback.content.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_from_url.return_value = mock_client

            from app.services.celery_tasks import get_redis_client
            result = get_redis_client()

            assert result == mock_client
            mock_from_url.assert_called_once()

    def test_uses_redis_url_constant(self):
        """Should use REDIS_URL module constant."""
        # Note: REDIS_URL is read at module import time, so we test
        # that get_redis_client uses whatever value is in the module
        from app.services.celery_tasks import REDIS_URL, get_redis_client

        with patch("app.services.voice_feedback.content.redis.from_url") as mock_from_url:
            mock_from_url.return_value = MagicMock()
            get_redis_client()

            # Should be called with the module's REDIS_URL constant
            mock_from_url.assert_called_with(REDIS_URL)


class TestContentDeduplication:
    """Test content deduplication functions.

    NOTE (Story 7): Dedup is now consolidated to FastAPI layer.
    See tests/test_dedup_consolidation.py for comprehensive dedup tests.
    Only content hash computation is tested here (still exported from celery_tasks).
    """

    def test_compute_content_hash(self):
        """Should compute consistent hash for same content."""
        from app.services.celery_tasks import _compute_content_hash

        content = "test content"
        hash1 = _compute_content_hash(content)
        hash2 = _compute_content_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated to 16 chars

    def test_compute_content_hash_different_content(self):
        """Should compute different hash for different content."""
        from app.services.celery_tasks import _compute_content_hash

        hash1 = _compute_content_hash("content A")
        hash2 = _compute_content_hash("content B")

        assert hash1 != hash2


# NOTE: TestSkipRole class removed - skip logic moved to app/services/skip_logic.py
# See tests/test_skip_logic.py for comprehensive skip logic tests
#
# NOTE (Story 7): Dedup tests removed from here - dedup is now at FastAPI layer
# See tests/test_dedup_consolidation.py for comprehensive dedup tests
