"""v1.0-r15 の簡易読み辞書補助機能を確認するテスト。"""

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

try:
    import sudachipy  # noqa: F401
except ModuleNotFoundError:
    fake_sudachi = types.ModuleType("sudachipy")
    fake_sudachi.dictionary = object()
    fake_sudachi.tokenizer = object()
    sys.modules["sudachipy"] = fake_sudachi

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from book_organize import cli
from book_organize.dictionary_assistant import (
    build_dictionary_candidates,
    check_reading_dictionary,
    extract_unresolved_authors,
    format_dictionary_candidates,
)
from book_organize.make_book_list import build_book_list_rows
from book_organize.reading_dictionary import load_reading_dictionary


class DictionaryAssistantR15Test(unittest.TestCase):
    def test_extract_unresolved_authors_deduplicates_and_ignores_missing_author(self):
        rows = [
            ["!!", "", "", "", "試験作者", "a.epub"],
            ["!!", "", "", "", "試験作者", "b.epub"],
            ["!!", "", "", "", "!!", "no-author.epub"],
            ["アア", "アア", "アイ", "アイ", "解決作者", "c.epub"],
        ]

        self.assertEqual(extract_unresolved_authors(rows), ["試験作者"])

    def test_format_dictionary_candidates_is_two_column_csv(self):
        text = format_dictionary_candidates(["カンマ,作者", "試験作者"])

        self.assertEqual(text, '"カンマ,作者",\n試験作者,\n')

    def test_build_dictionary_candidates_uses_existing_reading_dictionary(self):
        rows = [["!!", "", "", "", "試験作者", "sample.epub"]]
        reading_dict = {"試験作者": "シケンサクシャ"}

        with mock.patch(
            "book_organize.dictionary_assistant.build_book_list_rows",
            return_value=rows,
        ) as build:
            result = build_dictionary_candidates(
                "books",
                reading_dict=reading_dict,
            )

        self.assertEqual(result, ["試験作者"])
        build.assert_called_once_with(
            "books",
            short=False,
            reading_dict=reading_dict,
        )

    def test_check_reports_normalization_map_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "author-readings.csv"
            path.write_text("試験作者,ヴァッ\n", encoding="utf-8")

            result = check_reading_dictionary(path)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.entry_count, 1)
        self.assertEqual(
            result.normalization_changes,
            (("試験作者", "ヴァッ", "ウアツ"),),
        )
        self.assertEqual(result.invalid_entries, ())

    def test_check_flags_non_katakana_reading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "author-readings.csv"
            path.write_text("試験作者,漢字\n", encoding="utf-8")

            result = check_reading_dictionary(path)

        self.assertFalse(result.is_valid)
        self.assertEqual(
            result.invalid_entries,
            (("試験作者", "漢字", "漢字"),),
        )

    def test_dictionary_reading_uses_normalization_map_for_classification(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "[試験作者] sample.epub").write_bytes(b"")
            dictionary_path = root / "author-readings.csv"
            dictionary_path.write_text("試験作者,ｳﾞｧｯ\n", encoding="utf-8")
            reading_dict = load_reading_dictionary(dictionary_path)

            rows = build_book_list_rows(
                str(root),
                reading_dict=reading_dict,
            )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "アア")
        self.assertEqual(rows[0][1], "ウア")
        self.assertEqual(rows[0][2], "ウアツ")
        self.assertEqual(rows[0][3], "ヴァッ")
        self.assertEqual(rows[0][4], "試験作者")

    def test_cli_candidate_mode_writes_dictionary_candidates(self):
        candidates = ["試験作者"]
        with mock.patch.object(
            cli,
            "build_dictionary_candidates",
            return_value=candidates,
        ) as build:
            with mock.patch.object(cli, "write_dictionary_candidates") as write:
                result = cli.main(
                    [
                        "dict",
                        "--dir",
                        "books",
                        "--out",
                        "author-readings.todo.csv",
                    ]
                )

        self.assertEqual(result, 0)
        build.assert_called_once_with("books", reading_dict=None)
        write.assert_called_once_with(candidates, "author-readings.todo.csv")

    def test_cli_check_requires_reading_dictionary(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = cli.main(["dict", "--check"])

        self.assertEqual(result, 1)
        self.assertIn("--reading-dict", stderr.getvalue())

    def test_cli_check_reports_valid_dictionary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "author-readings.csv"
            path.write_text("試験作者,ヴァッ\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = cli.main(
                    ["dict", "--check", "--reading-dict", str(path)]
                )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("NORMALIZATION_MAP による変換: 1", output)
        self.assertIn("ヴァッ -> ウアツ", output)
        self.assertIn("判定: OK", output)

    def test_cli_check_rejects_invalid_reading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "author-readings.csv"
            path.write_text("試験作者,漢字\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = cli.main(
                    ["dict", "--check", "--reading-dict", str(path)]
                )

        self.assertEqual(result, 1)
        self.assertIn("無効な読み: 1", stderr.getvalue())
        self.assertIn("判定: NG", stderr.getvalue())

    def test_user_documentation_describes_dictionary_assistant(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        contract = (
            ROOT / "docs" / "development" / "PROJECT-CONTRACT.md"
        ).read_text(encoding="utf-8")

        self.assertIn("uv run book-organize.py dict", readme)
        self.assertIn("author-readings.todo.csv", readme)
        self.assertIn("dict --check", readme)
        self.assertIn("NORMALIZATION_MAP", readme)
        self.assertIn("| `dict` |", contract)

    def test_existing_dictionary_removes_resolved_author_from_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "[試験作者] sample.epub").write_bytes(b"")

            candidates = build_dictionary_candidates(
                str(root),
                reading_dict={"試験作者": "シケンサクシャ"},
            )

        self.assertEqual(candidates, [])

    def test_public_documents_do_not_expose_private_standards_name(self):
        paths = (
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "THIRD-PARTY-NOTICES.md",
            ROOT / "docs" / "development" / "PROJECT-CONTRACT.md",
            ROOT / "docs" / "development-baseline.md",
            ROOT / "docs" / "release-notes-v1.0.md",
            ROOT / "tools" / "release" / "README.md",
            ROOT / "tools" / "windows-build" / "README.md",
        )

        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("development-standards", text, path)


    def test_project_contract_preserves_revision_reset_wording(self):
        contract = (
            ROOT / "docs" / "development" / "PROJECT-CONTRACT.md"
        ).read_text(encoding="utf-8")

        self.assertIn("次の公開 version へ更新した時点", contract)
        self.assertIn("v1.0-r15", contract)


if __name__ == "__main__":
    unittest.main()
