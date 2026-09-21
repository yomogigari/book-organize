"""v1.0-r07 の完全なCLIヘルプを確認するテスト。"""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class CompleteHelpR07Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_sudachi = sys.modules.get("sudachipy")
        fake_sudachi = types.ModuleType("sudachipy")
        fake_sudachi.dictionary = object()
        fake_sudachi.tokenizer = object()
        sys.modules["sudachipy"] = fake_sudachi

        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))

        from book_organize import cli

        cls.cli = cli

    @classmethod
    def tearDownClass(cls):
        if cls.previous_sudachi is None:
            sys.modules.pop("sudachipy", None)
        else:
            sys.modules["sudachipy"] = cls.previous_sudachi

    def test_root_help_contains_all_subcommand_options(self):
        help_text = self.cli.create_parser().format_help()

        for option in (
            "--dir",
            "--short",
            "--out",
            "--reading-dict",
            "--csv",
            "--dry-run",
            "--first-dir",
        ):
            self.assertIn(option, help_text)

        self.assertIn("サブコマンド別の完全なヘルプ", help_text)
        self.assertIn("--- run ---", help_text)
        self.assertIn("--- list ---", help_text)
        self.assertIn("--- move ---", help_text)

    def test_each_subcommand_help_contains_its_options(self):
        parser = self.cli.create_parser()
        choices = None

        for action in parser._actions:
            action_choices = getattr(action, "choices", None)
            if isinstance(action_choices, dict) and {"run", "list", "move"}.issubset(
                action_choices
            ):
                choices = action_choices
                break

        self.assertIsNotNone(choices)

        run_help = choices["run"].format_help()
        list_help = choices["list"].format_help()
        move_help = choices["move"].format_help()

        for option in ("--dir", "--out", "--reading-dict", "--dry-run", "--first-dir"):
            self.assertIn(option, run_help)

        for option in ("--dir", "--short", "--out", "--reading-dict"):
            self.assertIn(option, list_help)

        for option in ("--dir", "--csv", "--dry-run", "--first-dir"):
            self.assertIn(option, move_help)

    def test_readme_documents_root_and_subcommand_help(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("uv run book-organize.py -h", readme)
        self.assertIn("uv run book-organize.py run -h", readme)
        self.assertIn("uv run book-organize.py list -h", readme)
        self.assertIn("uv run book-organize.py move -h", readme)


if __name__ == "__main__":
    unittest.main()
