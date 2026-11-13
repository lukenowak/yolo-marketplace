# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for the session-defaults script."""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugins" / "repo-ops" / "scripts" / "set-session-defaults.py"

EXPECTED = {
    "permissions": {
        "defaultMode": "bypassPermissions",
        "deny": [
            "SendMessage", "ListAgents", "mcp__claude_ai_Claude_Docs",
            "Artifact", "ArtifactComments", "ArtifactData",
        ],
    },
    "skipDangerousModePermissionPrompt": True,
    "feedbackSurveyRate": 0,
    "feedbackDrafts": "off",
    "crossSessionInbound": "refuse",
    "enabledPlugins": {"cc-plugin-privacy@builtin": False},
    "env": {
        "CLAUDE_CODE_DISABLE_MOUSE": "1",
        "IS_SANDBOX": "1",
        "DISABLE_TELEMETRY": "1",
        "DO_NOT_TRACK": "1",
    },
}


def load_script():
    spec = importlib.util.spec_from_file_location("set_session_defaults", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SettingsDefaultsTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()

    def test_fills_every_default_into_empty_settings(self):
        settings = {}
        self.module.apply_settings_defaults(settings)
        self.assertEqual(settings, EXPECTED)

    def test_keeps_unrelated_settings(self):
        settings = {
            "theme": "dark",
            "permissions": {"deny": ["WebFetch"], "allow": ["Bash(ls)"]},
            "env": {"FOO": "bar"},
            "enabledPlugins": {"other@market": True},
        }
        self.module.apply_settings_defaults(settings)
        self.assertEqual(settings["theme"], "dark")
        self.assertEqual(settings["permissions"]["allow"], ["Bash(ls)"])
        self.assertEqual(settings["permissions"]["deny"][0], "WebFetch")
        self.assertEqual(settings["env"]["FOO"], "bar")
        self.assertTrue(settings["enabledPlugins"]["other@market"])

    def test_lifts_the_auto_compact_switch_it_used_to_set(self):
        settings = {"env": {"DISABLE_AUTO_COMPACT": "1"}}
        self.module.apply_settings_defaults(settings)
        self.assertNotIn("DISABLE_AUTO_COMPACT", settings["env"])

    def test_keeps_auto_compact_off_when_opted_in(self):
        settings = {}
        self.module.apply_settings_defaults(settings, {"disable_auto_compact": True})
        self.assertEqual(settings["env"]["DISABLE_AUTO_COMPACT"], "1")

    def test_reports_no_change_once_applied(self):
        settings = {}
        self.assertTrue(self.module.apply_settings_defaults(settings))
        self.assertEqual(self.module.apply_settings_defaults(settings), [])


class MainTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.settings = self.home / ".claude" / "settings.json"
        self.claude_json = self.home / ".claude.json"
        for patcher in (
            mock.patch.object(self.module, "SETTINGS_PATH", self.settings),
            mock.patch.object(self.module, "CLAUDE_JSON_PATH", self.claude_json),
            mock.patch.object(self.module, "REPO_JSON_PATH", self.home / ".claude" / "repo.json"),
            mock.patch.object(Path, "home", return_value=self.home),
            mock.patch("sys.stdout", io.StringIO()),
            mock.patch("sys.stderr", io.StringIO()),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def read(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_creates_settings_when_missing(self):
        self.module.main()
        self.assertEqual(self.read(self.settings), EXPECTED)

    def test_leaves_invalid_settings_alone(self):
        self.settings.parent.mkdir(parents=True)
        self.settings.write_text("{not json", encoding="utf-8")
        self.module.main()
        self.assertEqual(self.settings.read_text(encoding="utf-8"), "{not json")

    def test_does_not_rewrite_settings_already_applied(self):
        self.settings.parent.mkdir(parents=True)
        text = json.dumps(EXPECTED)
        self.settings.write_text(text, encoding="utf-8")
        self.module.main()
        self.assertEqual(self.settings.read_text(encoding="utf-8"), text)

    def test_reads_opt_ins_from_repo_json(self):
        self.settings.parent.mkdir(parents=True)
        (self.home / ".claude" / "repo.json").write_text(
            json.dumps({"disable_auto_compact": True}), encoding="utf-8")
        self.module.main()
        self.assertEqual(self.read(self.settings)["env"]["DISABLE_AUTO_COMPACT"], "1")

    def test_marks_home_trusted(self):
        self.claude_json.write_text(json.dumps({"projects": {}}), encoding="utf-8")
        self.module.main()
        entry = self.read(self.claude_json)["projects"][str(self.home)]
        self.assertIs(entry["hasTrustDialogAccepted"], True)

    def test_does_not_create_claude_json(self):
        self.module.main()
        self.assertFalse(self.claude_json.exists())


if __name__ == "__main__":
    unittest.main()
