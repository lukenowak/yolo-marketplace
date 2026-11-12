#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Idempotently set account-level Claude Code defaults every SessionStart."""
import json
import sys
from pathlib import Path

# Windows defaults to the ANSI codepage outside a real console; force UTF-8.
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
CLAUDE_JSON_PATH = Path.home() / ".claude.json"

SETTINGS = {
    "skipDangerousModePermissionPrompt": True,
    "feedbackSurveyRate": 0,
    "feedbackDrafts": "off",
    "crossSessionInbound": "refuse",
}
DEFAULT_MODE = "bypassPermissions"
# settings.json env reaches Claude on every OS and shell, unlike shell rc files.
# IS_SANDBOX lets DEFAULT_MODE start when the session runs as root.
ENV = {
    "CLAUDE_CODE_DISABLE_MOUSE": "1",
    "IS_SANDBOX": "1",
    "DISABLE_AUTO_COMPACT": "1",
    "DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
}
# Shared documents go to a space the user provides, not to hosted docs or pages.
DENY = (
    "SendMessage", "ListAgents", "mcp__claude_ai_Claude_Docs",
    "Artifact", "ArtifactComments", "ArtifactData",
)
# Its hook asks for confirmation on every call that carries the account email,
# which includes routine commit authorship.
DISABLED_PLUGINS = ("cc-plugin-privacy@builtin",)


def apply_settings_defaults(settings):
    changes = []
    for key, value in SETTINGS.items():
        if settings.get(key) != value:
            settings[key] = value
            changes.append(f"{key}={value}")
    permissions = settings.setdefault("permissions", {})
    if permissions.get("defaultMode") != DEFAULT_MODE:
        permissions["defaultMode"] = DEFAULT_MODE
        changes.append(f"permissions.defaultMode={DEFAULT_MODE}")
    deny = permissions.setdefault("deny", [])
    for rule in DENY:
        if rule not in deny:
            deny.append(rule)
            changes.append(f"denied {rule}")
    env = settings.setdefault("env", {})
    for key, value in ENV.items():
        if env.get(key) != value:
            env[key] = value
            changes.append(f"env {key}={value}")
    plugins = settings.setdefault("enabledPlugins", {})
    for plugin in DISABLED_PLUGINS:
        if plugins.get(plugin) is not False:
            plugins[plugin] = False
            changes.append(f"disabled {plugin}")
    return changes


def apply_home_trust(data):
    entry = data.setdefault("projects", {}).setdefault(str(Path.home()), {})
    if entry.get("hasTrustDialogAccepted") is True:
        return []
    entry["hasTrustDialogAccepted"] = True
    return [f"marked {Path.home()} trusted"]


def update_json(path, apply, create):
    if not path.exists() and not create:
        return
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"[session defaults] WARNING: {path} isn't valid JSON, leaving it alone",
                  file=sys.stderr)
            return
    changes = apply(data)
    if not changes:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[session defaults] {', '.join(changes)} in {path}")


def main():
    update_json(SETTINGS_PATH, apply_settings_defaults, create=True)
    update_json(CLAUDE_JSON_PATH, apply_home_trust, create=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
