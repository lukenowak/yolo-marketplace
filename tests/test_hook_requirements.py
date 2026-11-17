# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests: hooks fail loudly when a required tool is missing, instead of
skipping with a warning nobody sees."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"


def script_hook_commands():
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    return [
        (event, h["command"])
        for event, groups in hooks.items()
        for group in groups
        for h in group["hooks"]
        if "/scripts/" in h["command"]
    ]


class HookRequirementsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()

    def path_with(self, *tools):
        bin_dir = self.root / "bin"
        bin_dir.mkdir(exist_ok=True)
        for tool in ("sh", *tools):
            (bin_dir / tool).symlink_to(shutil.which(tool))
        return str(bin_dir)

    def run_hook(self, command, path):
        return subprocess.run(
            [shutil.which("sh"), "-c", command],
            env={"PATH": path, "HOME": str(self.home),
                 "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
                 "CLAUDE_PLUGIN_DATA": str(self.root / "data")},
            cwd=self.home, input='{"session_id": "s"}', capture_output=True, text=True,
        )

    def test_script_hooks_exist(self):
        self.assertTrue(script_hook_commands())

    def test_missing_python_blocks_every_script_hook(self):
        path = self.path_with("curl")
        for event, command in script_hook_commands():
            with self.subTest(event=event, command=command):
                result = self.run_hook(command, path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("python3", result.stderr)

    def test_missing_curl_blocks_every_script_hook(self):
        path = self.path_with("python3")
        for event, command in script_hook_commands():
            with self.subTest(event=event, command=command):
                result = self.run_hook(command, path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("curl", result.stderr)

    def test_hooks_run_when_requirements_are_present(self):
        path = self.path_with("python3", "curl")
        for event, command in script_hook_commands():
            with self.subTest(event=event, command=command):
                result = self.run_hook(command, path)
                self.assertEqual(result.returncode, 0, result.stderr)


class ReadmeRequirementsTest(unittest.TestCase):
    def test_readme_lists_the_tools_hooks_require(self):
        readme = (PLUGIN.parents[1] / "README.md").read_text(encoding="utf-8")
        section = readme.split("### Requirements", 1)[1].split("\n#", 1)[0]
        for tool in ("python3", "curl"):
            self.assertIn(f"`{tool}`", section)


if __name__ == "__main__":
    unittest.main()
