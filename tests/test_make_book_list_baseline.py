"""作者名と読みの主要な変換規則を固定するテスト。"""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def load_script():
    """SudachiPyを呼び出さず、純粋な変換関数だけを読み込む。"""
    fake_sudachi = types.ModuleType("sudachipy")
    fake_sudachi.dictionary = object()
    fake_sudachi.tokenizer = object()

    previous = sys.modules.get("sudachipy")
    sys.modules["sudachipy"] = fake_sudachi
    try:
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from book_organize import make_book_list

        return make_book_list
    finally:
        if previous is None:
            sys.modules.pop("sudachipy", None)
        else:
            sys.modules["sudachipy"] = previous


class MakeBookListBaselineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_script()

    def test_extract_name_uses_first_bracket_and_stops_before_cross(self):
        filename = "(一般コミック) [サンプル作者×共同作者] サンプル 第01巻.zip"
        self.assertEqual(self.module.extract_name(filename), "サンプル作者")

    def test_extract_name_normalizes_full_width_latin_characters(self):
        self.assertEqual(self.module.extract_name("[ＡＢＣ] sample.epub"), "ABC")

    def test_extract_name_returns_marker_when_brackets_are_missing(self):
        self.assertEqual(self.module.extract_name("作者名なし.epub"), "!!")

    def test_normalize_katakana_preserves_current_rules(self):
        self.assertEqual(self.module.normalize_katakana("サンプルサクシャ"), "サンフルサクシヤ")
        self.assertEqual(self.module.normalize_katakana("キャット"), "キヤツト")

    def test_group_string_uses_first_two_normalized_kana_groups(self):
        self.assertEqual(
            self.module.build_group_string("ヨモキカリ", "サンプルサクシャ"),
            "ヤマ",
        )
        self.assertEqual(
            self.module.build_group_string("アカシロクロウ", "アカシロクロウ"),
            "アカ",
        )

    def test_non_katakana_group_is_detectable(self):
        self.assertTrue(self.module.is_katakana("アカ"))
        self.assertFalse(self.module.is_katakana("a-"))

    def test_escape_csv_field_preserves_current_quoting_rule(self):
        self.assertEqual(self.module.escape_csv_field("abc"), "abc")
        self.assertEqual(self.module.escape_csv_field("a,b"), '"a,b"')
        self.assertEqual(self.module.escape_csv_field('a"b'), '"a""b"')
        self.assertEqual(self.module.escape_csv_field("a'b"), '"a\'b"')


if __name__ == "__main__":
    unittest.main()
