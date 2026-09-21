"""v1.0-r02 のモジュール分離と従来エントリーポイントを確認するテスト。"""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def load_script(module_name: str, script_name: str):
    """ルートの互換エントリーポイントをモジュールとして読み込む。"""
    spec = importlib.util.spec_from_file_location(module_name, ROOT / script_name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModuleLayoutR02Test(unittest.TestCase):
    def test_core_modules_are_under_src_package(self):
        self.assertTrue((SRC / "book_organize" / "__init__.py").is_file())
        self.assertTrue((SRC / "book_organize" / "make_book_list.py").is_file())
        self.assertTrue((SRC / "book_organize" / "move_book.py").is_file())

    def test_make_book_list_entrypoint_delegates_to_core_module(self):
        fake_sudachi = types.ModuleType("sudachipy")
        fake_sudachi.dictionary = object()
        fake_sudachi.tokenizer = object()

        previous = sys.modules.get("sudachipy")
        sys.modules["sudachipy"] = fake_sudachi
        try:
            wrapper = load_script("make_book_list_entrypoint", "make-book-list.py")
            self.assertEqual(wrapper.main.__module__, "book_organize.make_book_list")
            self.assertEqual(wrapper.extract_name("[蓬がり] sample.epub"), "蓬がり")
        finally:
            if previous is None:
                sys.modules.pop("sudachipy", None)
            else:
                sys.modules["sudachipy"] = previous

    def test_move_book_entrypoint_delegates_to_core_module(self):
        wrapper = load_script("move_book_entrypoint", "move-book.py")
        self.assertEqual(wrapper.main.__module__, "book_organize.move_book")
        self.assertTrue(wrapper.is_valid_directory_code("アカ"))


if __name__ == "__main__":
    unittest.main()
