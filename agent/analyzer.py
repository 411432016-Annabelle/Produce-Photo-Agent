"""Runs claude -p on one photo (architecture section 3.4)."""

import asyncio
import json
import shutil
import tempfile
from pathlib import Path

from .config import PROJECT_ROOT

PROMPT_FILE = PROJECT_ROOT / "prompts" / "analyze_prompt.txt"
TIMEOUT_SECONDS = 120
PHOTO_NAME = "photo.jpg"


class AnalyzerError(Exception):
    """claude -p could not produce an answer. The message is a short reason for the Error row."""


def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def build_prompt(user_text: str) -> str:
    prompt = load_prompt()
    if user_text.strip():
        prompt += f"\nMessage from the uploader: {user_text}\n"
    return prompt


async def analyze_photo(
    jpeg_bytes: bytes,
    uploader_text: str,
    data_dir: Path,
    model: str,
    claude_bin: str = "claude",
) -> str:
    """Returns the raw stdout of claude -p. Raises AnalyzerError on failure or timeout."""
    # Defaults below are the unsafe behaviour; the GUARD blocks replace them.
    staging_dir = data_dir
    working_dir = data_dir
    cleanup_dir = None
    protective_args = []
    prompt_user_text = uploader_text

    # ==== GUARD 1: claude -p file scope isolation START ====
    # A fresh temp folder outside DATA_DIR holding only the one photo becomes the
    # working folder, and an explicit deny rule blocks reads of DATA_DIR by full path.
    staging_dir = Path(tempfile.mkdtemp(prefix="produce-check-"))
    working_dir = staging_dir
    cleanup_dir = staging_dir
    deny_settings = {"permissions": {"deny": [f"Read(/{data_dir.resolve()}/**)"]}}
    protective_args = [
        "--settings", json.dumps(deny_settings),
        "--setting-sources", "project",
        "--permission-mode", "default",
        "--strict-mcp-config",
        "--disable-slash-commands",
    ]
    # ==== GUARD 1 END ====

    # ==== GUARD 2: uploader text never reaches claude -p START ====
    # The uploader's text is data for the Note column only, never part of the prompt.
    prompt_user_text = ""
    # ==== GUARD 2 END ====

    prompt = build_prompt(prompt_user_text)
    command = [
        claude_bin, "-p",
        "--model", model,
        "--output-format", "json",
        "--no-session-persistence",
        *protective_args,
        "--tools", "Read",
    ]

    photo_path = staging_dir / PHOTO_NAME
    try:
        staging_dir.mkdir(parents=True, exist_ok=True)
        photo_path.write_bytes(jpeg_bytes)
        return await _run(command, prompt, working_dir)
    finally:
        photo_path.unlink(missing_ok=True)
        if cleanup_dir is not None:
            shutil.rmtree(cleanup_dir, ignore_errors=True)


async def _run(command: list[str], prompt: str, working_dir: Path) -> str:
    # The prompt goes in on stdin and the command is a list, so no shell ever
    # interprets any part of it.
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=working_dir,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        raise AnalyzerError("claude command not found") from None

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(prompt.encode("utf-8")), TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise AnalyzerError(f"claude -p timed out after {TIMEOUT_SECONDS} seconds") from None

    output = stdout.decode("utf-8", errors="replace")
    if process.returncode != 0 and not output.strip():
        detail = stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise AnalyzerError(f"claude -p failed: {detail[-1][:120] if detail else 'no details'}")
    # A non-zero exit that still printed an envelope is left to the contract check,
    # which reports the envelope's own error message.
    return output
