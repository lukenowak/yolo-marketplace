#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""PostToolUse: mirror plan files to the document space via docs_space.publish_command."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Windows defaults to the ANSI codepage outside a real console; force UTF-8.
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")

PLANS_DIR = Path.home() / ".claude" / "plans"
REPO_JSON_PATH = Path.home() / ".claude" / "repo.json"
# A hung publish would hold the session inside this hook.
TIMEOUT_SECONDS = 60
STDERR_TAIL_LINES = 5


def build_argv(template, file, title):
    argv = [arg.replace("{file}", file).replace("{title}", title) for arg in template]
    if argv and argv[0].startswith("~/"):
        argv[0] = str(Path.home() / argv[0][2:])
    return argv


def resolve_program(program):
    path = Path(program)
    if path.is_absolute():
        return program if path.is_file() or shutil.which(program) else None
    # Relative paths would resolve against the hook's cwd, which nothing fixes.
    if "/" in program or "\\" in program:
        return None
    return shutil.which(program)


def publish(template, file, title):
    argv = build_argv(template, file, title)
    if not argv or not resolve_program(argv[0]):
        program = argv[0] if argv else "(empty)"
        return False, f"publish_command program {program} is not absolute or on PATH"
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return False, f"publish_command timed out after {TIMEOUT_SECONDS}s"
    except OSError as error:
        return False, f"publish_command could not run: {error}"
    if result.returncode != 0:
        tail = "\n".join((result.stderr or "").strip().splitlines()[-STDERR_TAIL_LINES:])
        return False, f"publish_command failed (exit {result.returncode}):\n{tail}"
    lines = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]
    return True, lines[-1] if lines else ""


def read_json(stream_or_path):
    try:
        if isinstance(stream_or_path, Path):
            data = json.loads(stream_or_path.read_text(encoding="utf-8"))
        else:
            data = json.loads(stream_or_path.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def main():
    event = read_json(sys.stdin)
    file_path = (event.get("tool_input") or {}).get("file_path")
    if not file_path:
        return 0
    path = Path(file_path).resolve()
    if path.suffix != ".md" or path.parent != PLANS_DIR.resolve():
        return 0
    command = (read_json(REPO_JSON_PATH).get("docs_space") or {}).get("publish_command")
    if not command:
        return 0
    title = f"plans/{path.stem}"
    ok, message = publish(command, str(path), title)
    if not ok:
        print(f"[plan mirror] {title} not published: {message}", file=sys.stderr)
        return 2
    context = f"[plan mirror] published {title}" + (f": {message}" if message else "")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
