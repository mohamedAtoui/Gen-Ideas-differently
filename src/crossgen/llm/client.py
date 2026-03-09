"""LLM client wrapping `claude -p` CLI subprocess calls."""

from __future__ import annotations

import asyncio
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-6"


async def call_claude(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str | None = None,
) -> str:
    """Call Claude via the `claude -p` CLI and return the result text.

    Uses the Claude Code Max subscription — no API key needed.
    """
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--no-session-persistence",
        "--max-turns", "1",
        "--model", model,
    ]
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    logger.debug("Running: %s", " ".join(cmd[:6]) + "...")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode().strip()
        raise RuntimeError(f"claude -p failed (rc={proc.returncode}): {err_msg}")

    raw = stdout.decode().strip()

    # Parse JSON output format — extract the result text
    try:
        data = json.loads(raw)
        # claude --output-format json returns {"result": "...", ...}
        if isinstance(data, dict) and "result" in data:
            return data["result"]
        return raw
    except json.JSONDecodeError:
        return raw


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences from a string, if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    return cleaned


async def call_claude_json(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str | None = None,
    max_retries: int = 2,
    validation_errors: list[str] | None = None,
) -> dict:
    """Call Claude and parse the response as JSON.

    The prompt should instruct Claude to respond with valid JSON.

    Parameters
    ----------
    prompt:
        The user prompt to send.
    model:
        Model identifier to use.
    system_prompt:
        Optional system prompt.
    max_retries:
        Number of retries on JSON parse or validation failure (default 2).
    validation_errors:
        Optional list of validation error strings from a previous attempt.
        When provided on the *first* call these are included in the prompt so
        the LLM can correct its output.
    """
    current_prompt = prompt

    # If the caller already knows about validation errors, include them
    # in the very first attempt so the model can fix them immediately.
    if validation_errors:
        error_block = "\n".join(f"- {e}" for e in validation_errors)
        current_prompt += (
            "\n\nThe previous response had validation errors — please fix them:\n"
            f"{error_block}"
            "\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no explanation."
        )

    last_exception: Exception | None = None

    for attempt in range(1 + max_retries):
        text = await call_claude(
            current_prompt, model=model, system_prompt=system_prompt,
        )

        cleaned = _strip_code_fences(text)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            last_exception = exc
            if attempt < max_retries:
                logger.warning(
                    "JSON parse failed (attempt %d/%d): %s — retrying",
                    attempt + 1,
                    1 + max_retries,
                    exc,
                )
                # Append a stern JSON-only instruction for the retry
                current_prompt = (
                    prompt
                    + "\n\nIMPORTANT: Respond with ONLY valid JSON. "
                    "No markdown, no explanation."
                )

    # All retries exhausted
    raise last_exception  # type: ignore[misc]
