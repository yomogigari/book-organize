"""ファイル移動先の決定規則を固定するテスト。"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def load_script():
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from book_organize import move_book

    return move_book


class MoveBookBaselineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_script()

    def test_directory_code_accepts_two_katakana_characters(self):
        self.assertTrue(self.module.is_valid_directory_code("アカ"))
        self.assertTrue(self.module.is_valid_directory_code("ヤマ"))
        self.assertFalse(self.module.is_valid_directory_code("!!"))
        self.assertFalse(self.module.is_valid_directory_code("ア"))

    def test_directory_path_uses_two_levels_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            self.assertEqual(
                self.module.get_directory_path(base, "ヤマ"),
                base / "ヤ行" / "ヤマ",
            )

    def test_directory_path_can_use_first_level_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            self.assertEqual(
                self.module.get_directory_path(base, "ヤマ", first_dir=True),
                base / "ヤ行",
            )

    def test_process_file_moves_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            filename = "[明石六郎] sample.epub"
            source = base / filename
            source.write_text("sample", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                self.module.process_file(["アカ", filename], base)

            target = base / "ア行" / "アカ" / filename
            self.assertEqual(target.read_text(encoding="utf-8"), "sample")
            self.assertFalse(source.exists())
            self.assertIn("移動完了", stdout.getvalue())

    def test_process_file_skips_invalid_directory_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            filename = "[A-01] sample.zip"
            source = base / filename
            source.write_text("sample", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                self.module.process_file(["!!", filename], base)

            self.assertTrue(source.exists())
            self.assertIn("無効なディレクトリコード", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
