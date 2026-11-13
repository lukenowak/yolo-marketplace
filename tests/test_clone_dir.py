# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: development happens in a configurable clone location."""

import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


class CloneDirTest(unittest.TestCase):
    def test_config_template_has_a_per_repo_clone_dir(self):
        example = json.loads((PLUGIN / "repo.json.example").read_text(encoding="utf-8"))
        self.assertIn("{repo}", example["clone_dir"])

    def test_setup_clones_into_clone_dir(self):
        skill = (PLUGIN / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`clone_dir`", skill)
        self.assertIn("<home>/tmp/{repo}", skill)

    def test_rules_confine_development_to_clone_dir(self):
        rules = (PLUGIN / "rules.md").read_text(encoding="utf-8")
        self.assertIn("Develop only in `clone_dir`", rules)


if __name__ == "__main__":
    unittest.main()
