# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: one arena can hold task branches for several original repos."""

import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


class OriginalsTest(unittest.TestCase):
    def test_config_template_maps_repos_to_originals(self):
        example = json.loads((PLUGIN / "repo.json.example").read_text(encoding="utf-8"))
        self.assertNotIn("original_url", example)
        for entry in example["originals"].values():
            self.assertEqual(set(entry), {"url", "token_key"})

    def test_setup_records_several_originals(self):
        skill = (PLUGIN / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`originals`", skill)
        self.assertIn("`original_url`", skill)

    def test_rules_cut_each_repo_from_its_own_original(self):
        rules = (PLUGIN / "rules.md").read_text(encoding="utf-8")
        self.assertIn("`originals`", rules)
        self.assertIn("that original's default branch", rules)


if __name__ == "__main__":
    unittest.main()
