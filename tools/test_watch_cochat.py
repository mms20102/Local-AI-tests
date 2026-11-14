"""Offline tests for watch_cochat.py. They build a throwaway local origin and clone in a
temp folder; they never contact GitHub or a model.  Run:  python -B -m unittest tools/test_watch_cochat.py
"""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watch_cochat as w

MAIN, WORK = "origin/main", "origin/work"


def run(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                    "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
                   check=True, capture_output=True)


class WatcherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        root = Path(self.tmp.name)
        self.origin, self.author, self.clone = root / "origin.git", root / "author", root / "clone"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.author)],
                       check=True, capture_output=True)
        (self.author / "research").mkdir()
        self.commit("# log\n", branch="main", first=True)
        run(self.author, "branch", "work")
        run(self.author, "push", "-q", "origin", "main", "work")
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.clone)],
                       check=True, capture_output=True)
        self.inbox = root / "inbox"
        self.saved = (w.REPO, w.BRANCHES)
        w.REPO, w.BRANCHES = self.clone, (MAIN, WORK)
        self.state = {}
        self.assertEqual(self.check(), (0, ""))          # first run is a baseline only

    def tearDown(self):
        w.REPO, w.BRANCHES = self.saved
        self.tmp.cleanup()

    def commit(self, text, branch, path="research/co-chat.md", first=False):
        if not first:
            run(self.author, "checkout", "-q", branch)
        target = self.author / path
        target.parent.mkdir(exist_ok=True)
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        run(self.author, "add", "-A")
        run(self.author, "commit", "-q", "-m", "change")
        if not first:
            run(self.author, "push", "-q", "origin", branch)

    def check(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            count = w.check(self.inbox, self.state, False)
        return count, out.getvalue()

    def inbox_lines(self, reader):
        path = self.inbox / f"for-{reader}.jsonl"
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    def test_reply_goes_to_the_other_assistant_only(self):
        self.commit("\n### Q9 · ChatGPT asks Claude\ntext\n", "work")
        count, out = self.check()
        self.assertEqual(count, 1)
        self.assertIn("COCHAT new reply from ChatGPT", out)
        self.assertEqual(len(self.inbox_lines("claude")), 1)
        self.assertEqual(self.inbox_lines("chatgpt"), [])
        self.commit("\n### A9 · Claude answers Q9\ntext\n", "work")
        self.assertEqual(self.check()[0], 1)
        self.assertEqual(len(self.inbox_lines("claude")), 1)
        self.assertEqual(len(self.inbox_lines("chatgpt")), 1)
        self.assertTrue((self.inbox / "for-chatgpt-latest.md").exists())

    def test_main_catching_up_is_not_reported_again(self):
        self.commit("\n### A1 · ChatGPT answers\ntext\n", "work")
        self.assertEqual(self.check()[0], 1)
        run(self.author, "checkout", "-q", "main")
        run(self.author, "merge", "-q", "--ff-only", "work")
        run(self.author, "push", "-q", "origin", "main")
        self.assertEqual(self.check(), (0, ""))
        self.assertEqual(len(self.inbox_lines("claude")), 1)

    def test_same_commit_on_both_branches_is_one_event(self):
        self.commit("\n### A1 · ChatGPT answers\ntext\n", "work")
        run(self.author, "push", "-q", "origin", "work:main")
        count, out = self.check()
        self.assertEqual(count, 1)
        self.assertEqual(out.count("COCHAT"), 1)

    def test_commit_without_log_text_is_not_called_a_reply(self):
        self.commit("notes\n", "work", path="research/OTHER.md")
        count, out = self.check()
        self.assertEqual(count, 1)
        self.assertIn("repo update, no new log turns", out)
        self.assertNotIn("new reply", out)
        self.assertEqual(self.inbox_lines("claude")[0]["kind"], "files")
        self.assertFalse((self.inbox / "for-chatgpt-latest.md").exists())

    def test_failed_write_is_retried_and_delivered_once(self):
        self.commit("\n### A1 · ChatGPT answers\ntext\n", "work")
        real, calls = w.os.replace, []

        def failing(src, dst):
            calls.append(1)
            raise OSError("simulated disk failure")
        w.os.replace = failing
        try:
            with self.assertRaises(OSError):
                self.check()
        finally:
            w.os.replace = real
        self.assertTrue(calls)
        count, out = self.check()                       # same process, next poll
        self.assertEqual(count, 1)
        self.assertIn("COCHAT new reply from ChatGPT", out)
        self.assertEqual(len(self.inbox_lines("claude")), 1)   # not duplicated in the inbox
        self.assertEqual(self.check(), (0, ""))

    def test_fetch_failure_does_not_lose_the_event(self):
        self.commit("\n### A1 · ChatGPT answers\ntext\n", "work")
        real = w.git

        def broken(*args, **kwargs):
            if args and args[0] == "fetch":
                raise RuntimeError("simulated network failure")
            return real(*args, **kwargs)
        w.git = broken
        try:
            with self.assertRaises(RuntimeError):
                self.check()
        finally:
            w.git = real
        self.assertEqual(self.check()[0], 1)

    def test_since_replays_history(self):
        self.commit("\n### A1 · ChatGPT answers\ntext\n", "work")
        self.assertEqual(self.check()[0], 1)
        base = w.git("rev-parse", MAIN).strip()
        self.state.clear()
        self.state.update(heads={b: base for b in w.BRANCHES}, reported=[])
        self.assertEqual(self.check()[0], 1)

    def test_speaker_is_the_first_name_after_the_last_separator(self):
        self.assertEqual(w.speaker_of("Coordination request · ChatGPT to Claude — pending"), "ChatGPT")
        self.assertEqual(w.speaker_of("A6 · Claude answers Q6"), "Claude")
        self.assertEqual(w.speaker_of("Decision · Mohamed"), "Moderator")
        self.assertIsNone(w.speaker_of("Round 2 status"))


if __name__ == "__main__":
    unittest.main()
