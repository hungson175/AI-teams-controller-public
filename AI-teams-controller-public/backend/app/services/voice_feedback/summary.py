# -*- coding: utf-8 -*-
"""Summary generation for voice feedback.

Single Responsibility: Generate LLM summaries of task completions.
"""

import logging
import os

logger = logging.getLogger(__name__)


def generate_summary(
    original_command: str, pane_output: str, pre_trimmed: str | None = None
) -> str:
    """Generate voice-friendly summary from pane output using LLM.

    Args:
        original_command: The original voice command
        pane_output: Raw pane output (used if pre_trimmed not provided)
        pre_trimmed: Already trimmed output (to avoid duplicate trimming)

    Returns:
        Voice-friendly summary (2-3 sentences)
    """
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, SystemMessage

    from app.config.voice_constants import OUTPUT_TRUNCATE_LINES
    from app.services.voice_feedback.content import filter_hooks, trim_to_last_input

    # Check for API key
    if not os.environ.get("XAI_API_KEY"):
        logger.warning("[SUMMARY] XAI_API_KEY not set, using placeholder summary")
        return f"Done. Completed: {original_command[:50]}"

    llm = init_chat_model(
        "grok-4-fast-non-reasoning",
        model_provider="xai",
        temperature=0.3,
    )

    # Step 1: Use pre-trimmed if available, otherwise trim now
    trimmed_output = pre_trimmed if pre_trimmed else trim_to_last_input(pane_output)

    # Step 2: Smart hook detection - truncate at first hook marker
    filtered_output = filter_hooks(trimmed_output)

    # Get last N lines for context
    lines = filtered_output.split("\n")
    last_n_lines = "\n".join(lines[-OUTPUT_TRUNCATE_LINES:])

    messages = [
        SystemMessage(
            content="""You summarize AI assistant task completions for voice feedback.

CRITICAL: Output must be 2-3 SHORT sentences maximum. This is spoken aloud - be BRIEF.

LANGUAGE: Vietnamese mixed with English technical terms (code-switching style).
- Main language: Vietnamese
- Keep technical terms in English: component, class, API, endpoint, bug, commit, test, file, function, error, deploy, build, lint, etc.
- Style: Like a Vietnamese developer naturally mixing languages

FILTER OUT THESE (DO NOT summarize):
- Stop hook messages (lines with "Stop hook", "SessionStart hook", etc.)
- Memory store skill calls (lines with "coder-memory-store", "Skill tool", "storing patterns")
- Hook reminders (lines about "consider if valuable patterns discovered")
- System reminders and tool invocation metadata
- Any lines that start with "<system-reminder>" or mention hook execution

Rules:
1. Focus ONLY on the FINAL RESULT - what was accomplished
2. IGNORE all the intermediate steps, tool calls, file reads, searches
3. IGNORE all hook messages and skill invocation reminders
4. Start with "Xong rồi." or "Hoàn thành." then state what was achieved
5. If there was an error, say "Lỗi." and why briefly
6. Keep technical details minimal - just the outcome
7. NEVER include git commit IDs or hashes - they are meaningless when spoken aloud

Examples of GOOD summaries (Vietnamese mixed with English):
- "Xong rồi. Đã fix bug authentication trong login.py. Tests đã pass."
- "Hoàn thành. Đã tạo API endpoint mới cho user profiles."
- "Xong rồi. Tất cả 6 services đang chạy healthy."
- "Lỗi. Không tìm thấy file được chỉ định."
- "Hoàn thành. Đã update database schema và migrate data."

DO NOT include git commit IDs, file hashes, technical identifiers, or hook messages. Just the END RESULT.

Output in Vietnamese mixed with English technical terms, 2-3 SHORT sentences maximum."""
        ),
        HumanMessage(
            content=f"""User asked: {original_command}

Terminal output (scan for final result):
{last_n_lines}

Give 2-3 sentence summary of the FINAL RESULT only:"""
        ),
    ]

    response = llm.invoke(messages)
    return response.content.strip()
