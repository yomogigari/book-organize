"""v1.0-r05 のREADMEとCLIヘルプを確認するテスト。"""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class DocumentationR05Test(unittest.TestCase):
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

    def test_readme_uses_uv_run_for_unified_cli_examples(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("uv run book-organize.py run", readme)
        self.assertIn("uv run book-organize.py list", readme)
        self.assertIn("uv run book-organize.py move", readme)
        self.assertNotIn("python book-organize.py", readme)

    def test_readme_documents_reading_dictionary_and_dry_run(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("--reading-dict", readme)
        self.assertIn("サンプル作者,サンプルサクシャ", readme)
        self.assertIn("--dry-run", readme)
        self.assertIn("UTF-8 BOM", readme)

    def test_root_help_uses_script_name_and_uv_examples(self):
        help_text = self.cli.create_parser().format_help()

        self.assertIn("usage: book-organize.py", help_text)
        self.assertIn("uv run book-organize.py run", help_text)
        self.assertIn("uv run book-organize.py list", help_text)
        self.assertIn("uv run book-organize.py move", help_text)


if __name__ == "__main__":
    unittest.main()
