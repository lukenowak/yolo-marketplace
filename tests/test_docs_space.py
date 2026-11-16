# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: a provided document space is recorded, so later sessions reuse it."""

import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


class DocsSpaceTest(unittest.TestCase):
    def test_config_template_records_a_docs_space(self):
        example = json.loads((PLUGIN / "repo.json.example").read_text(encoding="utf-8"))
        self.assertEqual(set(example["docs_space"]), {"kind", "url", "token_key", "publish_command"})

    def test_rules_reuse_the_recorded_space_before_asking(self):
        rules = (PLUGIN / "rules.md").read_text(encoding="utf-8")
        self.assertIn("`docs_space`", rules)


if __name__ == "__main__":
    unittest.main()
