#!/usr/bin/env python3
"""This file owns the tests for guard-scope.py and its starter_config fallback.

The core regression: shlex keeps shell punctuation glued to a word, so
`ls /allowed/root;` used to be checked as "/allowed/root;" and blocked. These
cases fail on that unfixed tokenising and pass once punctuation is stripped.

Run: python3 -m unittest test_guard_scope   (from this directory)
  or python3 test_guard_scope.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_HOOK = _HERE / "guard-scope.py"

sys.path.insert(0, str(_HERE))
_spec = importlib.util.spec_from_file_location("guard_scope", str(_HOOK))
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)
import starter_config  # noqa: E402

PROJECT = "/home/user/code/project"
OTHER = "/home/user/private"


def roots():
    """Allowed roots for the Bash tests: just the fixture project.

    :return: list with the resolved fixture root.
    """
    return [Path(PROJECT).resolve()]


class TrailingPunctuationTest(unittest.TestCase):
    """An allowed root followed by shell punctuation must stay allowed.

    Each case puts the punctuation on the ROOT itself: on a child path
    ("root/src;") the glued name is still under the root, so it would pass
    even unfixed and prove nothing.
    """

    def assertAllowed(self, command):
        """Fail if the command has any out-of-scope token.

        :param command: Bash command text.
        :return: None
        """
        self.assertEqual(hook.out_of_scope_bash_tokens(command, roots()), [], command)

    def test_semicolon(self):
        """`ls /root;` is the reported bug."""
        self.assertAllowed("ls %s; echo done" % PROJECT)

    def test_ampersand(self):
        """A backgrounded command keeps `&` on the path."""
        self.assertAllowed("ls %s&" % PROJECT)

    def test_pipe(self):
        """A pipe without spaces glues `|` to the path."""
        self.assertAllowed("ls %s| head" % PROJECT)

    def test_subshell_parens(self):
        """`(cd /root)` glues `(` and `)`."""
        self.assertAllowed("(cd %s)" % PROJECT)

    def test_comma(self):
        """A comma-separated list keeps `,` on the path."""
        self.assertAllowed("echo %s, %s/b" % (PROJECT, PROJECT))


class StillBlocksTest(unittest.TestCase):
    """Stripping punctuation must not let an outside path through."""

    def test_outside_with_semicolon(self):
        """An outside path is still caught after its `;` is stripped."""
        self.assertEqual(hook.out_of_scope_bash_tokens("cat %s/key;" % OTHER, roots()),
                         ["%s/key;" % OTHER])

    def test_outside_in_subshell(self):
        """An outside path inside parentheses is still caught."""
        self.assertTrue(hook.out_of_scope_bash_tokens("(cat %s/key)" % OTHER, roots()))

    def test_home_parent_blocked(self):
        """The parent of an allowed root is not allowed."""
        self.assertTrue(hook.out_of_scope_bash_tokens("ls /home/user;", roots()))


class ConfigFallbackTest(unittest.TestCase):
    """A missing config narrows the guard to the session cwd, never crashes."""

    def setUp(self):
        """Point STARTER_CONFIG at a file that does not exist.

        :return: None
        """
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.environ.get(starter_config.CONFIG_ENV_VAR)
        os.environ[starter_config.CONFIG_ENV_VAR] = os.path.join(self.tmp.name, "missing.json")

    def tearDown(self):
        """Restore the environment.

        :return: None
        """
        if self.old is None:
            os.environ.pop(starter_config.CONFIG_ENV_VAR, None)
        else:
            os.environ[starter_config.CONFIG_ENV_VAR] = self.old
        self.tmp.cleanup()

    def test_load_returns_none(self):
        """No file means None, not an exception."""
        self.assertIsNone(starter_config.load_config())

    def test_roots_without_config(self):
        """Only system roots plus the cwd are allowed."""
        got = hook.allowed_roots(Path(PROJECT), None)
        self.assertIn(Path(PROJECT).resolve(), got)
        self.assertNotIn(Path("/home/user/code").resolve(), got)

    def test_config_adds_workspace(self):
        """A config's workspace_root and extra_roots are added."""
        cfg_path = os.path.join(self.tmp.name, "cfg.json")
        with open(cfg_path, "w") as fh:
            json.dump({"workspace_root": "/home/user/code", "extra_roots": ["/home/user/notes"]}, fh)
        os.environ[starter_config.CONFIG_ENV_VAR] = cfg_path
        cfg = starter_config.load_config()
        got = hook.allowed_roots(Path(PROJECT), cfg)
        self.assertIn(Path("/home/user/code").resolve(), got)
        self.assertIn(Path("/home/user/notes").resolve(), got)
        self.assertEqual([Path("~/.agents").expanduser().resolve()], cfg.readonly_roots)

    def test_hook_hint_and_allow_in_cwd(self):
        """End to end: missing config prints the hint and still allows the cwd."""
        event = {"tool_name": "Read", "tool_input": {"file_path": PROJECT + "/a.txt"}, "cwd": PROJECT}
        proc = subprocess.run([sys.executable, str(_HOOK)], input=json.dumps(event).encode(),
                              capture_output=True, env=dict(os.environ))
        self.assertEqual(proc.returncode, 0)
        self.assertIn(b"run install.sh", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
