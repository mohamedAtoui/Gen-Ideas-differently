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


async def call_claude_json(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt: str | None = None,
) -> dict:
    """Call Claude and parse the response as JSON.

    The prompt should instruct Claude to respond with valid JSON.
    """
    text = await call_claude(prompt, model=model, system_prompt=system_prompt)

    # Try to extract JSON from the response (handle markdown code blocks)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove markdown code fence
        lines = cleaned.split("\n")
        # Drop first and last lines (``` markers)
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    return json.loads(cleaned)
