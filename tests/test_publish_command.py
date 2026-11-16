# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: documents are published through the layer's command."""

import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class PublishCommandConfigTest(unittest.TestCase):
    def test_config_template_has_a_publish_command(self):
        example = json.loads((PLUGIN / "repo.json.example").read_text(encoding="utf-8"))
        command = example["docs_space"]["publish_command"]
        self.assertIn("{file}", command)
        self.assertIn("{title}", command)

    def test_setup_records_the_publish_command(self):
        self.assertIn("`publish_command`", flat(PLUGIN / "skills" / "setup" / "SKILL.md"))

    def test_rules_publish_through_the_command_when_set(self):
        rules = flat(PLUGIN / "rules.md")
        self.assertIn("publish through `docs_space.publish_command`", rules)
        self.assertIn("non-zero exit is a failed publish", rules)
