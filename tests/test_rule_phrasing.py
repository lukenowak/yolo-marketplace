# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: rules follow the phrasing guide."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE = REPO_ROOT / "docs" / "rule-phrasing.md"
RULES = REPO_ROOT / "plugins" / "repo-ops" / "rules.md"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class RulePhrasingTest(unittest.TestCase):
    def test_guide_states_each_principle(self):
        text = flat(GUIDE)
        for heading in ("## Positive scope first", "## Attach the why",
                        "## Glue negatives to their replacement",
                        "## Bare NEVER only for one-safe-path invariants"):
            self.assertIn(heading, text, heading)

    def test_readme_points_rule_authors_to_the_guide(self):
        self.assertIn("docs/rule-phrasing.md", flat(REPO_ROOT / "README.md"))

    def test_commit_content_rule_names_what_belongs(self):
        text = flat(RULES)
        self.assertNotIn("not a diff summary; never `Co-Authored-By`", text)
        self.assertIn("Commits hold text you wrote", text)

    def test_default_branch_rule_names_where_work_goes(self):
        self.assertIn("push work to task branches instead", flat(RULES))


if __name__ == "__main__":
    unittest.main()
