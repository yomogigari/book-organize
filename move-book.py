#!/usr/bin/env python
# coding: utf-8
"""従来の move-book.py コマンドを維持する互換エントリーポイント。"""

from __future__ import annotations

import sys
from pathlib import Path


_SRC_DIR = Path(__file__).resolve().parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from book_organize.move_book import (  # noqa: E402
    get_directory_path,
    is_valid_directory_code,
    main,
    process_file,
)


if __name__ == "__main__":
    main()
