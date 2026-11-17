# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression test: the session's working directory stays at home, so deleting a
scratch directory never targets the working directory or its ancestor, which asks for
confirmation even when permission prompts are off."""

import unittest
from pathlib import Path


RULES = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops" / "rules.md"


class WorkingDirectoryRuleTest(unittest.TestCase):
    def test_rules_keep_the_working_directory_at_home(self):
        text = " ".join(RULES.read_text(encoding="utf-8").split())
        for phrase in ("Keep the shell's working directory at `<home>`", "`git -C <dir>`",
                       "`( cd <dir> && ... )`", "even with permission prompts off"):
            self.assertIn(phrase, text, phrase)


if __name__ == "__main__":
    unittest.main()
