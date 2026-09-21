#!/usr/bin/env python
# coding: utf-8
"""book-organize の統合コマンドを提供する。"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from .make_book_list import build_book_list_rows, write_csv_rows
from .move_book import process_rows, read_csv_rows
from .reading_dictionary import ReadingDictionaryError, load_reading_dictionary


def create_parser() -> argparse.ArgumentParser:
    """統合CLIの引数パーサーを作成する。"""
    parser = argparse.ArgumentParser(
        prog="book-organize.py",
        description="電子書籍ファイルを作者名の読みに基づいて分類・整理します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "実行例:\n"
            "  uv run book-organize.py run --dir E:\\E-book --dry-run\n"
            "  uv run book-organize.py list --dir E:\\E-book --out book-list.csv\n"
            "  uv run book-organize.py move --dir E:\\E-book --csv book-list.csv --dry-run"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list",
        help="分類用の一覧を生成します。",
        description="ファイル名から作者名の読みを生成し、分類用のCSVを出力します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "実行例:\n"
            "  uv run book-organize.py list --dir E:\\E-book --out book-list.csv\n"
            "  uv run book-organize.py list --dir E:\\E-book "
            "--reading-dict author-readings.csv --out book-list.csv"
        ),
    )
    list_parser.add_argument(
        "--dir",
        type=str,
        default=os.getcwd(),
        help="対象ディレクトリ。指定がなければ起動ディレクトリを使用",
    )
    list_parser.add_argument("--short", action="store_true", help="短縮形式で出力")
    list_parser.add_argument(
        "--out",
        type=str,
        help="出力先ファイル名。指定がなければ標準出力に出力",
    )
    _add_reading_dictionary_option(list_parser)

    move_parser = subparsers.add_parser(
        "move",
        help="CSVに従ってファイルを移動します。",
        description="分類用CSVの情報に基づいてファイルを移動します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "実行例:\n"
            "  uv run book-organize.py move --dir E:\\E-book "
            "--csv book-list.csv --dry-run"
        ),
    )
    move_parser.add_argument("--csv", type=str, required=True, help="入力CSVファイル（必須）")
    move_parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="処理を行うベースディレクトリ（必須）",
    )
    _add_move_options(move_parser)

    run_parser = subparsers.add_parser(
        "run",
        help="一覧生成とファイル移動を続けて実行します。",
        description=(
            "対象ディレクトリから分類情報を生成し、その結果を使ってファイルを移動します。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "実行例:\n"
            "  uv run book-organize.py run --dir E:\\E-book --dry-run\n"
            "  uv run book-organize.py run --dir E:\\E-book "
            "--reading-dict author-readings.csv --dry-run"
        ),
    )
    run_parser.add_argument(
        "--dir",
        type=str,
        default=os.getcwd(),
        help="対象ディレクトリ。指定がなければ起動ディレクトリを使用",
    )
    run_parser.add_argument("--short", action="store_true", help="短縮形式で分類情報を生成")
    run_parser.add_argument(
        "--out",
        type=str,
        help="生成した分類用CSVの保存先。指定しない場合は保存しない",
    )
    _add_reading_dictionary_option(run_parser)
    _add_move_options(run_parser)
    return parser


def _add_reading_dictionary_option(parser: argparse.ArgumentParser) -> None:
    """作者名の読み補正に使う簡易CSV辞書のオプションを追加する。"""
    parser.add_argument(
        "--reading-dict",
        type=str,
        help="作者名と読みを2列で記述した簡易CSV辞書",
    )


def _add_move_options(parser: argparse.ArgumentParser) -> None:
    """move と run に共通する移動オプションを追加する。"""
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを移動せず、実行予定の処理を表示",
    )
    parser.add_argument(
        "--first-dir",
        action="store_true",
        help="最初の階層ディレクトリのみを使用してファイルを移動",
    )


def _configure_utf8_output() -> None:
    """Windowsでも日本語の標準出力をUTF-8で扱えるようにする。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def _load_optional_reading_dictionary(path: str | None) -> dict[str, str] | None:
    """指定されている場合だけ簡易読み辞書を読み込む。"""
    if not path:
        return None
    return load_reading_dictionary(path)


def _run_list(args: argparse.Namespace) -> int:
    reading_dict = _load_optional_reading_dictionary(args.reading_dict)
    if reading_dict is None:
        rows = build_book_list_rows(args.dir, short=args.short)
    else:
        rows = build_book_list_rows(
            args.dir,
            short=args.short,
            reading_dict=reading_dict,
        )
    write_csv_rows(rows, args.out)
    return 0


def _run_move(args: argparse.Namespace) -> int:
    if not os.path.isdir(args.dir):
        print(f"エラー: 指定されたディレクトリが存在しません: {args.dir}", file=sys.stderr)
        return 1

    rows = read_csv_rows(args.csv)
    process_rows(rows, args.dir, dry_run=args.dry_run, first_dir=args.first_dir)
    return 0


def _run_combined(args: argparse.Namespace) -> int:
    reading_dict = _load_optional_reading_dictionary(args.reading_dict)
    if reading_dict is None:
        rows = build_book_list_rows(args.dir, short=args.short)
    else:
        rows = build_book_list_rows(
            args.dir,
            short=args.short,
            reading_dict=reading_dict,
        )
    if args.out:
        write_csv_rows(rows, args.out)
    process_rows(rows, args.dir, dry_run=args.dry_run, first_dir=args.first_dir)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """引数を解析し、指定されたサブコマンドを実行する。"""
    _configure_utf8_output()
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            return _run_list(args)
        if args.command == "move":
            return _run_move(args)
        if args.command == "run":
            return _run_combined(args)
    except NotADirectoryError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1
    except ReadingDictionaryError as exc:
        print(f"読み辞書エラー: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ファイル処理エラー: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"予期しないエラー: {exc}", file=sys.stderr)
        return 1

    parser.error(f"未対応のコマンドです: {args.command}")
    return 2
