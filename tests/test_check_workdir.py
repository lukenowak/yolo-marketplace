# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for the workdir check."""

import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugins" / "repo-ops" / "scripts" / "check-workdir.py"


def load_script():
    spec = importlib.util.spec_from_file_location("check_workdir", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DocsDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name).resolve()
        for patcher in (
            mock.patch.object(Path, "home", return_value=self.home),
            mock.patch.object(Path, "cwd", return_value=self.home),
            mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": str(self.home / "data")}),
            mock.patch("sys.argv", ["check-workdir.py"]),
            mock.patch("sys.stdin", io.StringIO('{"session_id": "s"}')),
            mock.patch("sys.stdout", io.StringIO()),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_does_not_create_a_docs_directory(self):
        self.assertEqual(self.module.main(), 0)
        self.assertTrue((self.home / "tmp").is_dir())
        self.assertFalse((self.home / "docs").exists())


if __name__ == "__main__":
    unittest.main()
