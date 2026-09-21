"""v1.0-r06 の未変換読み検出を確認するテスト。"""

from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class _Token:
    def __init__(self, reading: str):
        self._reading = reading

    def reading_form(self) -> str:
        return self._reading


class _Tokenizer:
    def __init__(self, reading: str):
        self.reading = reading

    def tokenize(self, name, mode):
        return [_Token(self.reading)]


class ReadingValidationR06Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_sudachi = sys.modules.get("sudachipy")
        fake_sudachi = types.ModuleType("sudachipy")
        fake_sudachi.dictionary = types.SimpleNamespace(Dictionary=object)
        fake_sudachi.tokenizer = types.SimpleNamespace(
            Tokenizer=types.SimpleNamespace(SplitMode=types.SimpleNamespace(C=object()))
        )
        sys.modules["sudachipy"] = fake_sudachi
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from book_organize import make_book_list

        cls.module = make_book_list

    @classmethod
    def tearDownClass(cls):
        if cls.previous_sudachi is None:
            sys.modules.pop("sudachipy", None)
        else:
            sys.modules["sudachipy"] = cls.previous_sudachi

    def test_partial_unconverted_reading_is_invalid(self):
        self.assertFalse(self.module.is_complete_katakana_reading("オオヌマタカシ揮"))
        self.assertTrue(self.module.is_complete_katakana_reading("オオヌマタカシキ"))
        self.assertFalse(self.module.is_complete_katakana_reading(""))

    def test_partial_unconverted_sudachi_result_marks_row_as_unclassified(self):
        fake_dictionary = mock.Mock()
        fake_dictionary.create.return_value = _Tokenizer("オオヌマタカシ揮")

        fake_dictionary_module = types.SimpleNamespace(
            Dictionary=mock.Mock(return_value=fake_dictionary)
        )
        fake_tokenizer_module = types.SimpleNamespace(
            Tokenizer=types.SimpleNamespace(
                SplitMode=types.SimpleNamespace(C=object())
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "[大沼隆揮] sample.epub"
            (Path(temp_dir) / filename).write_text("sample", encoding="utf-8")
            with mock.patch.object(self.module, "dictionary", fake_dictionary_module):
                with mock.patch.object(self.module, "tokenizer", fake_tokenizer_module):
                    rows = self.module.build_book_list_rows(temp_dir)

        self.assertEqual(rows[0][0], "!!")
        self.assertEqual(rows[0][2], "オオヌマタカシ揮")
        self.assertEqual(rows[0][4], "大沼隆揮")

    def test_reading_dictionary_can_correct_partial_unconverted_reading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "[大沼隆揮] sample.epub"
            (Path(temp_dir) / filename).write_text("sample", encoding="utf-8")
            rows = self.module.build_book_list_rows(
                temp_dir,
                reading_dict={"大沼隆揮": "オオヌマタカシキ"},
            )

        self.assertNotEqual(rows[0][0], "!!")
        self.assertEqual(rows[0][2], "オオヌマタカシキ")
        self.assertEqual(rows[0][3], "オオヌマタカシキ")


if __name__ == "__main__":
    unittest.main()
