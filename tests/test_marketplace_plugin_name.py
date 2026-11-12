# SPDX-License-Identifier: GPL-3.0-or-later
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "repo-ops"


class MarketplacePluginNameTest(unittest.TestCase):
    def test_marketplace_lists_the_plugin_once(self):
        marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        names = [p["name"] for p in marketplace["plugins"]]
        self.assertEqual(names, [PLUGIN_NAME])

    def test_plugin_manifest_matches(self):
        manifest = json.loads(
            (REPO_ROOT / "plugins" / PLUGIN_NAME / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], PLUGIN_NAME)
        self.assertNotIn("version", manifest)


if __name__ == "__main__":
    unittest.main()
