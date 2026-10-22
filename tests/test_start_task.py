"""Integration checks against disposable Git repositories; no network required."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "start-task.py"
IGNORE = SCRIPT.parent.parent / ".gitignore"


class TaskWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.repo = self.parent / "project"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "shared.txt").write_text("original\n")
        self.git("add", "shared.txt")
        self.git("commit", "-m", "Initial")

    def git(self, *args, cwd=None, check=True):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, text=True,
                              capture_output=True, check=check)

    def start(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              cwd=cwd or self.repo, text=True, capture_output=True)

    def checkout(self, owner, task):
        return self.parent / "project-worktrees" / owner / task

    def test_parallel_tasks_preserve_staged_and_untracked_work(self):
        (self.repo / "shared.txt").write_text("someone else's staged work\n")
        self.git("add", "shared.txt")
        (self.repo / "notes.txt").write_text("private scratch\n")
        before = self.git("status", "--porcelain").stdout
        for owner in ("alice", "bob"):
            result = self.start(owner, "feature")
            self.assertEqual(result.returncode, 0, result.stderr)
            checkout = self.checkout(owner, "feature")
            self.assertEqual((checkout / "shared.txt").read_text(), "original\n")
            self.assertEqual(self.git("branch", "--show-current", cwd=checkout).stdout.strip(),
                             f"agent/{owner}/feature")
        (self.checkout("alice", "feature") / "shared.txt").write_text("alice's change\n")
        self.assertEqual((self.checkout("bob", "feature") / "shared.txt").read_text(), "original\n")
        self.assertEqual(self.git("status", "--porcelain").stdout, before)
        self.assertEqual((self.repo / "shared.txt").read_text(), "someone else's staged work\n")

    def test_duplicate_and_invalid_names_are_rejected(self):
        self.assertEqual(self.start("alice", "feature").returncode, 0)
        target = self.checkout("alice", "feature") / "shared.txt"
        target.write_text("in progress\n")
        self.assertNotEqual(self.start("alice", "feature").returncode, 0)
        self.assertEqual(target.read_text(), "in progress\n")
        for owner in ("../escape", "--force", "Alice", "a/b"):
            self.assertNotEqual(self.start(owner, "feature").returncode, 0)

    def test_existing_branch_and_invalid_base_leave_no_checkout(self):
        self.git("branch", "agent/alice/existing")
        self.assertNotEqual(self.start("alice", "existing").returncode, 0)
        self.assertNotEqual(self.start("alice", "missing", "--base", "missing").returncode, 0)
        self.assertFalse(self.checkout("alice", "existing").exists())
        self.assertFalse(self.checkout("alice", "missing").exists())

    def test_invocation_from_linked_checkout(self):
        self.assertEqual(self.start("alice", "first").returncode, 0)
        result = self.start("bob", "second", cwd=self.checkout("alice", "first"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.checkout("bob", "second").is_dir())

    def test_remote_default_and_existing_remote_task(self):
        remote = self.parent / "remote.git"
        self.git("init", "--bare", "-b", "develop", str(remote))
        self.git("branch", "-m", "develop")
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "develop")
        result = self.start("alice", "remote")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git("branch", "agent/bob/taken")
        self.git("push", "origin", "agent/bob/taken")
        self.git("branch", "-D", "agent/bob/taken")
        self.assertNotEqual(self.start("bob", "taken").returncode, 0)
        self.assertFalse(self.checkout("bob", "taken").exists())

    def test_ignore_secrets_but_keep_lockfiles_and_instructions(self):
        (self.repo / ".gitignore").write_text(IGNORE.read_text())
        for name in (".env", ".env.local", "node_modules/test.js", ".venv/bin/python", ".worktrees/task/file"):
            self.assertEqual(self.git("check-ignore", name, check=False).returncode, 0, name)
        for name in (".env.example", "package-lock.json", "uv.lock", "AGENTS.md", "CLAUDE.md"):
            self.assertEqual(self.git("check-ignore", name, check=False).returncode, 1, name)


if __name__ == "__main__":
    unittest.main()
