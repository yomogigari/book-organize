#!/usr/bin/env python
# coding: utf-8
"""従来の make-book-list.py コマンドを維持する互換エントリーポイント。"""

from __future__ import annotations

import sys
from pathlib import Path


_SRC_DIR = Path(__file__).resolve().parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from book_organize.make_book_list import (  # noqa: E402
    KANA_GROUPS,
    NORMALIZATION_MAP,
    TARGET_EXTENSIONS,
    build_group_string,
    escape_csv_field,
    extract_name,
    get_kana_group,
    is_katakana,
    main,
    normalize_katakana,
)


if __name__ == "__main__":
    main()
