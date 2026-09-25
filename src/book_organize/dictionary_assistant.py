#!/usr/bin/env python
# coding: utf-8
"""簡易読み辞書の作成と検査を補助する。"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence

from .make_book_list import (
    build_book_list_rows,
    is_complete_katakana_reading,
    normalize_katakana,
)
from .reading_dictionary import load_reading_dictionary


@dataclass(frozen=True)
class DictionaryCheckResult:
    """簡易読み辞書の検査結果。"""

    entry_count: int
    normalization_changes: tuple[tuple[str, str, str], ...]
    invalid_entries: tuple[tuple[str, str, str], ...]

    @property
    def is_valid(self) -> bool:
        """分類に使用できない読みがなければ True を返す。"""
        return not self.invalid_entries


def extract_unresolved_authors(rows: Sequence[Sequence[str]]) -> list[str]:
    """分類コードが ``!!`` の行から辞書で補正できる作者名を抽出する。"""
    authors = {
        row[4]
        for row in rows
        if len(row) >= 6 and row[0] == "!!" and row[4] != "!!"
    }
    return sorted(authors)


def build_dictionary_candidates(
    target_dir: str,
    *,
    reading_dict: dict[str, str] | None = None,
) -> list[str]:
    """対象ディレクトリを分類し、未解決の作者名を重複なく返す。"""
    rows = build_book_list_rows(
        target_dir,
        short=False,
        reading_dict=reading_dict,
    )
    return extract_unresolved_authors(rows)


def format_dictionary_candidates(authors: Sequence[str]) -> str:
    """作者名を ``作者名,`` 形式の 2 列 CSV へ変換する。"""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for author in authors:
        writer.writerow([author, ""])
    return output.getvalue()


def write_dictionary_candidates(
    authors: Sequence[str],
    output_path: str | Path | None = None,
) -> None:
    """辞書候補 CSV をファイルへ保存するか、標準出力へ出力する。"""
    output_text = format_dictionary_candidates(authors)
    if output_path:
        Path(output_path).write_text(output_text, encoding="utf-8", newline="")
    else:
        print(output_text, end="")


def check_reading_dictionary(path: str | Path) -> DictionaryCheckResult:
    """辞書の読みが分類用正規化後も有効なカタカナか確認する。"""
    entries = load_reading_dictionary(path)
    normalization_changes: list[tuple[str, str, str]] = []
    invalid_entries: list[tuple[str, str, str]] = []

    for author in sorted(entries):
        raw_reading = entries[author]
        normalized_reading = normalize_katakana(raw_reading)
        if normalized_reading != raw_reading:
            normalization_changes.append(
                (author, raw_reading, normalized_reading)
            )
        if not is_complete_katakana_reading(normalized_reading):
            invalid_entries.append(
                (author, raw_reading, normalized_reading)
            )

    return DictionaryCheckResult(
        entry_count=len(entries),
        normalization_changes=tuple(normalization_changes),
        invalid_entries=tuple(invalid_entries),
    )
