#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Run a plugin script with Python. Exit 2 when Python or curl (which setup and
# document sharing rely on) is missing: Claude Code shows a hook's stderr to the user
# on exit 2, and blocks the prompt in UserPromptSubmit, so the session can't go on
# without the defaults and checks these hooks enforce.
PY=$(command -v python3 || command -v python || command -v py)
if [ -z "$PY" ]; then
    echo "[repo-ops] ERROR: python3 not found on PATH. Install python3 and restart Claude Code." >&2
    exit 2
fi
if ! command -v curl >/dev/null; then
    echo "[repo-ops] ERROR: curl not found on PATH. Install curl and restart Claude Code." >&2
    exit 2
fi
script=$1
shift
exec "$PY" "${0%/*}/$script" "$@"
