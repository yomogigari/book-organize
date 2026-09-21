"""v1.0-r04 の簡易読み辞書を確認するテスト。"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class ReadingDictionaryR04Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_sudachi = sys.modules.get("sudachipy")
        fake_sudachi = types.ModuleType("sudachipy")
        fake_sudachi.dictionary = object()
        fake_sudachi.tokenizer = types.SimpleNamespace(
            Tokenizer=types.SimpleNamespace(SplitMode=types.SimpleNamespace(C=object()))
        )
        sys.modules["sudachipy"] = fake_sudachi

        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))

        from book_organize import cli, make_book_list, reading_dictionary

        cls.cli = cli
        cls.make_book_list = make_book_list
        cls.reading_dictionary = reading_dictionary

    @classmethod
    def tearDownClass(cls):
        if cls.previous_sudachi is None:
            sys.modules.pop("sudachipy", None)
        else:
            sys.modules["sudachipy"] = cls.previous_sudachi

    def test_loads_utf8_bom_and_normalizes_author_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readings.csv"
            path.write_text("\ufeff蓬がり,ヨモギガリ\nＡＢＣ,ｴｰﾋﾞｰｼｰ\n", encoding="utf-8")

            result = self.reading_dictionary.load_reading_dictionary(path)

        self.assertEqual(result["蓬がり"], "ヨモギガリ")
        self.assertEqual(result["ABC"], "エービーシー")

    def test_ignores_blank_lines(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readings.csv"
            path.write_text("\n蓬がり,ヨモギガリ\n\n", encoding="utf-8")

            result = self.reading_dictionary.load_reading_dictionary(path)

        self.assertEqual(result, {"蓬がり": "ヨモギガリ"})

    def test_rejects_empty_author(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readings.csv"
            path.write_text(",ヨモギガリ\n", encoding="utf-8")

            with self.assertRaisesRegex(
                self.reading_dictionary.ReadingDictionaryError,
                "作者名が空",
            ):
                self.reading_dictionary.load_reading_dictionary(path)

    def test_rejects_duplicate_author_after_normalization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readings.csv"
            path.write_text("ＡＢＣ,エービーシー\nABC,エービーシー\n", encoding="utf-8")

            with self.assertRaisesRegex(
                self.reading_dictionary.ReadingDictionaryError,
                "重複",
            ):
                self.reading_dictionary.load_reading_dictionary(path)

    def test_rejects_rows_other_than_two_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readings.csv"
            path.write_text("蓬がり,ヨモギガリ,extra\n", encoding="utf-8")

            with self.assertRaisesRegex(
                self.reading_dictionary.ReadingDictionaryError,
                "2列",
            ):
                self.reading_dictionary.load_reading_dictionary(path)

    def test_dictionary_reading_takes_priority_over_sudachi(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            book = Path(temp_dir) / "[蓬がり] sample.epub"
            book.touch()
            fake_dictionary = types.SimpleNamespace(Dictionary=mock.Mock())

            with mock.patch.object(self.make_book_list, "dictionary", fake_dictionary):
                rows = self.make_book_list.build_book_list_rows(
                    temp_dir,
                    reading_dict={"蓬がり": "ヨモギガリ"},
                )

        fake_dictionary.Dictionary.assert_not_called()
        self.assertEqual(rows[0][2], "ヨモキカリ")
        self.assertEqual(rows[0][3], "ヨモギガリ")
        self.assertEqual(rows[0][4], "蓬がり")

    def test_unregistered_author_uses_sudachi(self):
        token = mock.Mock()
        token.reading_form.return_value = "ミト"
        sudachi_tokenizer = mock.Mock()
        sudachi_tokenizer.tokenize.return_value = [token]
        dictionary_instance = mock.Mock()
        dictionary_instance.create.return_value = sudachi_tokenizer
        fake_dictionary = types.SimpleNamespace(
            Dictionary=mock.Mock(return_value=dictionary_instance)
        )

        fake_tokenizer_module = types.SimpleNamespace(
            Tokenizer=types.SimpleNamespace(SplitMode=types.SimpleNamespace(C=object()))
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "[水戸] sample.epub").touch()
            with mock.patch.object(self.make_book_list, "dictionary", fake_dictionary):
                with mock.patch.object(
                    self.make_book_list,
                    "tokenizer",
                    fake_tokenizer_module,
                ):
                    rows = self.make_book_list.build_book_list_rows(
                        temp_dir,
                        reading_dict={"蓬がり": "ヨモギガリ"},
                    )

        fake_dictionary.Dictionary.assert_called_once_with(dict="full")
        self.assertEqual(rows[0][3], "ミト")

    def test_list_command_passes_reading_dictionary(self):
        rows = [["ヤマ", "sample.epub"]]
        readings = {"蓬がり": "ヨモギガリ"}
        with mock.patch.object(
            self.cli,
            "load_reading_dictionary",
            return_value=readings,
        ) as load:
            with mock.patch.object(
                self.cli,
                "build_book_list_rows",
                return_value=rows,
            ) as build:
                with mock.patch.object(self.cli, "write_csv_rows"):
                    result = self.cli.main(
                        ["list", "--dir", "books", "--reading-dict", "readings.csv"]
                    )

        self.assertEqual(result, 0)
        load.assert_called_once_with("readings.csv")
        build.assert_called_once_with("books", short=False, reading_dict=readings)

    def test_cli_reports_reading_dictionary_format_error(self):
        error = self.reading_dictionary.ReadingDictionaryError("2行目が不正です。")
        stderr = io.StringIO()
        with mock.patch.object(
            self.cli,
            "load_reading_dictionary",
            side_effect=error,
        ):
            with contextlib.redirect_stderr(stderr):
                result = self.cli.main(
                    ["list", "--dir", "books", "--reading-dict", "readings.csv"]
                )

        self.assertEqual(result, 1)
        self.assertIn("読み辞書エラー", stderr.getvalue())

    def test_run_command_passes_reading_dictionary(self):
        rows = [["ヤマ", "sample.epub"]]
        readings = {"蓬がり": "ヨモギガリ"}
        with mock.patch.object(
            self.cli,
            "load_reading_dictionary",
            return_value=readings,
        ):
            with mock.patch.object(
                self.cli,
                "build_book_list_rows",
                return_value=rows,
            ) as build:
                with mock.patch.object(self.cli, "process_rows"):
                    result = self.cli.main(
                        ["run", "--dir", "books", "--reading-dict", "readings.csv"]
                    )

        self.assertEqual(result, 0)
        build.assert_called_once_with("books", short=False, reading_dict=readings)


if __name__ == "__main__":
    unittest.main()
