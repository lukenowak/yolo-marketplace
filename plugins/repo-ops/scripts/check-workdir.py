#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Enforce the session launched from <home>; keep <home>/tmp present.

Judges the recorded launch cwd (marker file keyed by session_id), not live cwd, so a
later `cd` mid-session doesn't trigger a false block.

  check-workdir.py            SessionStart: create dirs, record launch cwd, warn only
  check-workdir.py --block    UserPromptSubmit: exit 2 if launch cwd wasn't home
"""
import json
import os
import sys
import time
from pathlib import Path

# Windows defaults to the ANSI codepage outside a real console; force UTF-8.
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")

MARKER_MAX_AGE_SECONDS = 7 * 24 * 3600


def marker_dir():
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    directory = Path(env) if env else Path.home() / ".claude" / "workdir-check"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def marker_path(directory, session_id):
    return directory / f"launch-cwd-{session_id or 'unknown'}.txt"


def purge_stale_markers(directory):
    cutoff = time.time() - MARKER_MAX_AGE_SECONDS
    for marker in directory.glob("launch-cwd-*.txt"):
        try:
            if marker.stat().st_mtime < cutoff:
                marker.unlink()
        except OSError:
            pass


def read_hook_input():
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def main():
    block_mode = "--block" in sys.argv
    home = Path.home().resolve()
    tmp = home / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    session_id = read_hook_input().get("session_id")
    directory = marker_dir()
    path = marker_path(directory, session_id)

    if block_mode:
        if not path.exists():
            return 0
        launch_cwd = Path(path.read_text(encoding="utf-8").strip())
        if launch_cwd == home:
            return 0
        print(
            f"[workdir check] BLOCKED: session was launched from {launch_cwd}, not the "
            f"top-level user directory ({home}). Exit and relaunch from {home} -- this "
            f"can't be fixed mid-session. Scratch clones belong under {tmp}, never a "
            f"shared /tmp.",
            file=sys.stderr,
        )
        return 2

    purge_stale_markers(directory)
    if not path.exists():
        path.write_text(str(Path.cwd().resolve()), encoding="utf-8")
    launch_cwd = Path(path.read_text(encoding="utf-8").strip())

    if launch_cwd == home:
        print(f"[workdir check] OK: cwd is the top-level user directory ({home}); {tmp} present.")
    else:
        print(
            f"[workdir check] WARNING: session launched from {launch_cwd}, not the "
            f"top-level user directory ({home}). Exit and relaunch from {home} -- this "
            f"can't be fixed mid-session. Scratch clones belong under {tmp}, never a "
            f"shared /tmp.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
