# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for mirroring plan files through docs_space.publish_command."""

import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "repo-ops"
SCRIPT = PLUGIN / "scripts" / "publish-plan.py"


def load_script():
    spec = importlib.util.spec_from_file_location("publish_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess([], returncode, stdout=stdout, stderr=stderr)


class BuildArgvTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()

    def test_substitutes_file_and_title_inside_arguments(self):
        argv = self.module.build_argv(
            ["/opt/layer/publish", "{file}", "--title={title}"], "/p/a b.md", "plans/x: y")
        self.assertEqual(argv, ["/opt/layer/publish", "/p/a b.md", "--title=plans/x: y"])

    def test_leaves_other_braces_alone(self):
        argv = self.module.build_argv(["/bin/pub", "{other}", "{file}"], "/f", "t")
        self.assertEqual(argv, ["/bin/pub", "{other}", "/f"])

    def test_expands_home_in_program(self):
        with mock.patch.object(Path, "home", return_value=Path("/home/u")):
            argv = self.module.build_argv(["~/bin/publish", "{file}"], "/f", "t")
        self.assertEqual(argv[0], str(Path("/home/u/bin/publish")))


class PublishTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        which = mock.patch("shutil.which", side_effect=lambda name: f"/usr/bin/{name}")
        which.start()
        self.addCleanup(which.stop)

    def test_success_returns_the_printed_url(self):
        with mock.patch("subprocess.run", return_value=completed(
                stdout="uploading\nhttps://docs.example.com/plans/x\n")) as run:
            ok, message = self.module.publish(["publish", "{file}", "{title}"], "/f", "plans/x")
        self.assertTrue(ok)
        self.assertEqual(message, "https://docs.example.com/plans/x")
        self.assertEqual(run.call_args.args[0], ["publish", "/f", "plans/x"])
        self.assertIsNotNone(run.call_args.kwargs.get("timeout"))
        self.assertNotIn("shell", run.call_args.kwargs)

    def test_non_zero_exit_fails_with_stderr_tail(self):
        stderr = "\n".join(f"line {i}" for i in range(20))
        with mock.patch("subprocess.run", return_value=completed(3, stderr=stderr)):
            ok, message = self.module.publish(["publish", "{file}"], "/f", "t")
        self.assertFalse(ok)
        self.assertIn("exit 3", message)
        self.assertIn("line 19", message)
        self.assertNotIn("line 0\n", message)

    def test_timeout_fails(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("publish", 60)):
            ok, message = self.module.publish(["publish", "{file}"], "/f", "t")
        self.assertFalse(ok)
        self.assertIn("timed out", message)

    def test_unresolvable_program_fails_without_running(self):
        with mock.patch("shutil.which", return_value=None), \
                mock.patch("subprocess.run") as run:
            ok, message = self.module.publish(["bin/publish", "{file}"], "/f", "t")
        self.assertFalse(ok)
        self.assertIn("bin/publish", message)
        run.assert_not_called()


class HookTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        self.plans = home / ".claude" / "plans"
        self.plans.mkdir(parents=True)
        self.plan = self.plans / "tidy-branches.md"
        self.plan.write_text("# Plan\n", encoding="utf-8")
        self.repo_json = home / ".claude" / "repo.json"
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        for patcher in (
            mock.patch.object(self.module, "PLANS_DIR", self.plans),
            mock.patch.object(self.module, "REPO_JSON_PATH", self.repo_json),
            mock.patch("sys.stdout", self.stdout),
            mock.patch("sys.stderr", self.stderr),
            mock.patch("shutil.which", side_effect=lambda name: f"/usr/bin/{name}"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def configure(self, command):
        space = {"kind": "x", "url": "https://docs.example.com/"}
        if command is not None:
            space["publish_command"] = command
        self.repo_json.write_text(json.dumps({"docs_space": space}), encoding="utf-8")

    def run_hook(self, path, tool="Write"):
        event = {"hook_event_name": "PostToolUse", "tool_name": tool,
                 "tool_input": {"file_path": str(path)}}
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))):
            return self.module.main()

    def test_publishes_plan_under_plans_title_and_reports_url(self):
        self.configure(["publish", "{file}", "{title}"])
        with mock.patch("subprocess.run",
                        return_value=completed(stdout="https://docs.example.com/p\n")) as run:
            self.assertEqual(self.run_hook(self.plan, tool="Edit"), 0)
        self.assertEqual(run.call_args.args[0],
                         ["publish", str(self.plan.resolve()), "plans/tidy-branches"])
        context = json.loads(self.stdout.getvalue())["hookSpecificOutput"]["additionalContext"]
        self.assertIn("https://docs.example.com/p", context)

    def test_failed_publish_exits_2_with_reason(self):
        self.configure(["publish", "{file}", "{title}"])
        with mock.patch("subprocess.run", return_value=completed(1, stderr="denied")):
            self.assertEqual(self.run_hook(self.plan), 2)
        self.assertIn("denied", self.stderr.getvalue())

    def test_without_publish_command_does_nothing(self):
        self.configure(None)
        with mock.patch("subprocess.run") as run:
            self.assertEqual(self.run_hook(self.plan), 0)
        run.assert_not_called()
        self.assertEqual(self.stdout.getvalue() + self.stderr.getvalue(), "")

    def test_without_repo_json_does_nothing(self):
        with mock.patch("subprocess.run") as run:
            self.assertEqual(self.run_hook(self.plan), 0)
        run.assert_not_called()

    def test_ignores_files_outside_plans(self):
        self.configure(["publish", "{file}", "{title}"])
        other = Path(self.tmp.name) / "notes.md"
        other.write_text("x", encoding="utf-8")
        with mock.patch("subprocess.run") as run:
            self.assertEqual(self.run_hook(other), 0)
        run.assert_not_called()


class HookRegistrationTest(unittest.TestCase):
    def test_runs_after_write_and_edit(self):
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        groups = hooks["hooks"]["PostToolUse"]
        matching = [g for g in groups
                    if any("publish-plan.py" in h["command"] for h in g["hooks"])]
        self.assertEqual(len(matching), 1)
        self.assertEqual(set(matching[0]["matcher"].split("|")), {"Write", "Edit", "MultiEdit"})


if __name__ == "__main__":
    unittest.main()
