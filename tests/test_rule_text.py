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

    def test_development_loop_waits_for_ci_itself(self):
        text = rules()
        for phrase in ("## Development loop", "scheduled self-wakeup",
                       "never ask the user to check back later", "*pre-existing*",
                       "*infrastructure*", "\"flake\" is not a verdict",
                       "two fix attempts without measurable progress"):
            self.assertIn(phrase, text, phrase)

    def test_external_references_carry_full_urls(self):
        self.assertIn("Give every external reference its full URL at least once in the same "
                      "message", rules())

    def test_messages_lead_with_the_conclusion(self):
        self.assertIn("Lead with the conclusion", rules())

    def test_times_are_reported_in_the_configured_zone(self):
        self.assertIn("`timezone`", rules())
        self.assertIn("label only a deliberately foreign zone", rules())

    def test_setup_records_the_timezone(self):
        skill = (RULES.parent / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
        example = (RULES.parent / "repo.json.example").read_text(encoding="utf-8")
        self.assertIn("`timezone`", skill)
        self.assertIn('"timezone"', example)

    def test_development_loop_skips_arenas_without_ci(self):
        self.assertIn("If the push starts no CI run, the local test run is the verdict",
                      rules())

if __name__ == "__main__":
    unittest.main()
