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
REPO_JSON_PATH = Path.home() / ".claude" / "repo.json"

SETTINGS = {
    "skipDangerousModePermissionPrompt": True,
    "feedbackSurveyRate": 0,
    "feedbackDrafts": "off",
    "crossSessionInbound": "refuse",
    "spinnerTipsEnabled": False,
}
DEFAULT_MODE = "bypassPermissions"
# settings.json env reaches Claude on every OS and shell, unlike shell rc files.
# IS_SANDBOX lets DEFAULT_MODE start when the session runs as root.
ENV = {
    "CLAUDE_CODE_DISABLE_MOUSE": "1",
    "IS_SANDBOX": "1",
    "DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
}
# Long autonomous loops outlive the context window; compaction stays on unless
# repo.json opts out. Earlier versions forced it off, so lift that value.
AUTO_COMPACT_ENV = "DISABLE_AUTO_COMPACT"
# Shared documents go to a space the user provides, not to hosted docs or pages.
DENY = (
    "SendMessage", "ListAgents", "mcp__claude_ai_Claude_Docs",
    "Artifact", "ArtifactComments", "ArtifactData",
)
# Its hook asks for confirmation on every call that carries the account email,
# which includes routine commit authorship.
DISABLED_PLUGINS = ("cc-plugin-privacy@builtin",)


def apply_settings_defaults(settings, config=None):
    config = config or {}
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
    removed = list(config.get("deny_remove") or [])
    for rule in [*DENY, *(config.get("deny_extra") or [])]:
        if rule not in removed and rule not in deny:
            deny.append(rule)
            changes.append(f"denied {rule}")
    for rule in removed:
        if rule in deny:
            deny.remove(rule)
            changes.append(f"allowed {rule}")
    env = settings.setdefault("env", {})
    for key, value in ENV.items():
        if env.get(key) != value:
            env[key] = value
            changes.append(f"env {key}={value}")
    if config.get("disable_auto_compact") is True:
        if env.get(AUTO_COMPACT_ENV) != "1":
            env[AUTO_COMPACT_ENV] = "1"
            changes.append(f"env {AUTO_COMPACT_ENV}=1")
    elif env.get(AUTO_COMPACT_ENV) == "1":
        del env[AUTO_COMPACT_ENV]
        changes.append(f"removed env {AUTO_COMPACT_ENV}")
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


def read_config():
    try:
        config = json.loads(REPO_JSON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return config if isinstance(config, dict) else {}


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
    config = read_config()
    update_json(SETTINGS_PATH, lambda s: apply_settings_defaults(s, config), create=True)
    update_json(CLAUDE_JSON_PATH, apply_home_trust, create=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
