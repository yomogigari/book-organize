"""v1.0-r03 の統合CLIを確認するテスト。"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class UnifiedCliR03Test(unittest.TestCase):
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

    def test_unified_entrypoint_delegates_to_cli_module(self):
        spec = importlib.util.spec_from_file_location(
            "book_organize_entrypoint",
            ROOT / "book-organize.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.main.__module__, "book_organize.cli")

    def test_parser_provides_expected_subcommands(self):
        parser = self.cli.create_parser()
        self.assertEqual(parser.parse_args(["list"]).command, "list")
        self.assertEqual(
            parser.parse_args(["move", "--csv", "books.csv", "--dir", "."]).command,
            "move",
        )
        self.assertEqual(parser.parse_args(["run"]).command, "run")
        self.assertEqual(parser.parse_args(["dict"]).command, "dict")

    def test_list_command_generates_and_outputs_rows(self):
        rows = [["ヤマ", "sample.epub"]]
        with mock.patch.object(self.cli, "build_book_list_rows", return_value=rows) as build:
            with mock.patch.object(self.cli, "write_csv_rows") as write:
                result = self.cli.main(["list", "--dir", "books", "--short", "--out", "list.csv"])

        self.assertEqual(result, 0)
        build.assert_called_once_with("books", short=True)
        write.assert_called_once_with(rows, "list.csv")

    def test_move_command_reads_csv_and_processes_rows(self):
        rows = [["ヤマ", "sample.epub"]]
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(self.cli, "read_csv_rows", return_value=rows) as read:
                with mock.patch.object(self.cli, "process_rows") as process:
                    result = self.cli.main(
                        [
                            "move",
                            "--csv",
                            "books.csv",
                            "--dir",
                            temp_dir,
                            "--dry-run",
                            "--first-dir",
                        ]
                    )

        self.assertEqual(result, 0)
        read.assert_called_once_with("books.csv")
        process.assert_called_once_with(rows, temp_dir, dry_run=True, first_dir=True)

    def test_run_command_uses_generated_rows_for_move(self):
        rows = [["ヤマ", "sample.epub"]]
        with mock.patch.object(self.cli, "build_book_list_rows", return_value=rows) as build:
            with mock.patch.object(self.cli, "write_csv_rows") as write:
                with mock.patch.object(self.cli, "process_rows") as process:
                    result = self.cli.main(
                        [
                            "run",
                            "--dir",
                            "books",
                            "--short",
                            "--out",
                            "list.csv",
                            "--dry-run",
                        ]
                    )

        self.assertEqual(result, 0)
        build.assert_called_once_with("books", short=True)
        write.assert_called_once_with(rows, "list.csv")
        process.assert_called_once_with(rows, "books", dry_run=True, first_dir=False)

    def test_run_command_does_not_write_csv_without_out_option(self):
        rows = [["ヤマ", "sample.epub"]]
        with mock.patch.object(self.cli, "build_book_list_rows", return_value=rows):
            with mock.patch.object(self.cli, "write_csv_rows") as write:
                with mock.patch.object(self.cli, "process_rows") as process:
                    result = self.cli.main(["run", "--dir", "books"])

        self.assertEqual(result, 0)
        write.assert_not_called()
        process.assert_called_once_with(rows, "books", dry_run=False, first_dir=False)


if __name__ == "__main__":
    unittest.main()
