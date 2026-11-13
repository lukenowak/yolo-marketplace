# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for rules that are prose only."""

import unittest
from pathlib import Path


RULES = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops" / "rules.md"


def rules():
    return " ".join(RULES.read_text(encoding="utf-8").split())


class RuleTextTest(unittest.TestCase):
    def test_tdd_rule_is_language_neutral(self):
        self.assertNotIn("unittest.mock", rules())
        self.assertIn("the language's standard mocking library", rules())


    def test_own_branch_failures_are_in_scope(self):
        self.assertIn("Fixing failures of your own task branch, CI failures included, is "
                      "within scope", rules())

if __name__ == "__main__":
    unittest.main()
