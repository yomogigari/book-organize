"""v1.0-r10 の公開テストデータ匿名化を確認するテスト。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".ps1",
    ".toml",
    ".txt",
}

LEGACY_TEST_TERMS = (
    "\u5927\u6cbc\u9686\u63ee",
    "\u30aa\u30aa\u30cc\u30de\u30bf\u30ab\u30b7\u63ee",
    "\u30aa\u30aa\u30cc\u30de\u30bf\u30ab\u30b7\u30ad",
    "\u30aa\u30aa\u30cc\u30de\u30bf\u30ab\u30b7",
    "\u9999\u6708\u7f8e\u591c",
    "\u84ec\u304c\u308a",
    "\u30e8\u30e2\u30ae\u30ac\u30ea",
    "\u3088\u3082\u30fc\u304e",
)

SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "book-organize.py",
    ROOT / "src",
    ROOT / "tests",
    ROOT / "tools",
    ROOT / "docs",
)


def iter_public_text_files():
    """公開リポジトリでテスト例を含み得るテキストファイルを列挙する。"""
    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        if root.is_file():
            if root.suffix.lower() in TEXT_SUFFIXES:
                yield root
            continue

        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                yield path


class PublicTestDataR10Test(unittest.TestCase):
    def test_legacy_person_like_test_terms_are_absent(self):
        found: list[str] = []

        for path in iter_public_text_files():
            text = path.read_text(encoding="utf-8-sig")
            for term in LEGACY_TEST_TERMS:
                if term in text:
                    found.append(
                        f"{path.relative_to(ROOT).as_posix()}: {term}"
                    )

        self.assertEqual([], found, "\n".join(found))


if __name__ == "__main__":
    unittest.main()
