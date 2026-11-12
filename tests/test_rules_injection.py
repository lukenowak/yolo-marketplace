# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: rules reach the session through SessionStart output, not a skill
the model has to be nudged into loading."""

import json
import subprocess
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


def hook_commands(event):
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    return [h["command"] for group in hooks.get(event, []) for h in group["hooks"]]


class RulesInjectionTest(unittest.TestCase):
    def test_session_start_prints_the_rules(self):
        rules = (PLUGIN / "rules.md").read_text(encoding="utf-8")
        printing = [c for c in hook_commands("SessionStart") if "rules.md" in c]
        self.assertEqual(len(printing), 1)
        out = subprocess.run(
            ["sh", "-c", printing[0]], env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN)},
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertEqual(out, rules)

    def test_no_skill_nudge_remains(self):
        self.assertFalse(any("check-skill-invoked" in c for c in hook_commands("UserPromptSubmit")))


if __name__ == "__main__":
    unittest.main()
