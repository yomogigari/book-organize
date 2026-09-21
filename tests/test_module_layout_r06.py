"""v1.0-r06 の統合CLI構成を確認するテスト。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class ModuleLayoutR06Test(unittest.TestCase):
    def test_core_modules_are_under_src_package(self):
        self.assertTrue((SRC / "book_organize" / "__init__.py").is_file())
        self.assertTrue((SRC / "book_organize" / "make_book_list.py").is_file())
        self.assertTrue((SRC / "book_organize" / "move_book.py").is_file())

    def test_unified_entrypoint_is_the_only_root_cli(self):
        self.assertTrue((ROOT / "book-organize.py").is_file())
        self.assertFalse((ROOT / "make-book-list.py").exists())
        self.assertFalse((ROOT / "move-book.py").exists())


if __name__ == "__main__":
    unittest.main()
