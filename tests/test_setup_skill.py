# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: people hand over repos and tokens; Claude does the setup."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN = REPO_ROOT / "plugins" / "repo-ops"
SKILL = PLUGIN / "skills" / "setup" / "SKILL.md"


class SetupSkillTest(unittest.TestCase):
    def test_skill_has_frontmatter_at_byte_zero(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: setup\ndescription:"))

    def test_skill_covers_every_config_key(self):
        text = SKILL.read_text(encoding="utf-8")
        for key in ("arena_url", "arena_token_key", "original_url", "docs_space", "no-main"):
            self.assertIn(key, text, key)

    def test_rules_point_to_the_skill(self):
        self.assertIn("repo-ops:setup", (PLUGIN / "rules.md").read_text(encoding="utf-8"))

    def test_readme_leaves_config_editing_to_the_agent(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("repo.json.example", readme)
        self.assertNotIn("repo_tokens.json", readme)


if __name__ == "__main__":
    unittest.main()
