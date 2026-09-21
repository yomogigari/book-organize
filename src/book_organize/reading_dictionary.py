#!/usr/bin/env python
# coding: utf-8
"""作者名の読みを補正する簡易CSV辞書を読み込む。"""

from __future__ import annotations

import csv
import unicodedata
from pathlib import Path


class ReadingDictionaryError(ValueError):
    """簡易読み辞書の内容が不正な場合に送出する。"""


def normalize_author_name(value: str) -> str:
    """ファイル名から抽出した作者名と同じ基準で比較用文字列を整える。"""
    return unicodedata.normalize("NFKC", value.strip())


def normalize_reading(value: str) -> str:
    """半角カタカナなどを全角へそろえ、前後の空白を除去する。"""
    return unicodedata.normalize("NFKC", value.strip())


def load_reading_dictionary(path: str | Path) -> dict[str, str]:
    """2列CSVから作者名と読みの対応表を読み込む。

    CSVはヘッダーなしで ``作者名,ヨミ`` の2列とする。空行は無視する。
    UTF-8とUTF-8 BOM付きの両方を受け付ける。
    """
    result: dict[str, str] = {}
    dictionary_path = Path(path)

    with dictionary_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        for line_number, row in enumerate(reader, start=1):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) != 2:
                raise ReadingDictionaryError(
                    f"{line_number}行目は2列で指定してください: 作者名,ヨミ"
                )

            author = normalize_author_name(row[0])
            reading = normalize_reading(row[1])
            if not author:
                raise ReadingDictionaryError(f"{line_number}行目の作者名が空です。")
            if not reading:
                raise ReadingDictionaryError(f"{line_number}行目の読みが空です。")
            if author in result:
                raise ReadingDictionaryError(
                    f"{line_number}行目の作者名が重複しています: {author}"
                )

            result[author] = reading

    return result
