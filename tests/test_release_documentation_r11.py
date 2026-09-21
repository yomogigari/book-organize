"""v1.0-r11 の公開文書を確認するテスト。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseDocumentationR11Test(unittest.TestCase):
    def test_release_documents_exist(self):
        for path in (
            ROOT / "CHANGELOG.md",
            ROOT / "THIRD-PARTY-NOTICES.md",
            ROOT / "docs" / "release-notes-v1.0.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_readme_documents_windows_release(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("book-organize-v1.0-windows-x64.zip", readme)
        self.assertIn("%LOCALAPPDATA%\\book-organize\\v1.0", readme)
        self.assertIn("THIRD-PARTY-NOTICES.md", readme)
        self.assertIn("SHA256SUMS.txt", readme)

    def test_changelog_has_unreleased_v1_section(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("## v1.0 — Unreleased", changelog)
        self.assertIn("最初の正式リリース", changelog)
        self.assertIn("SudachiPy 0.6.11", changelog)
        self.assertIn("SudachiDict-full 20260723", changelog)

    def test_release_notes_document_safe_usage(self):
        notes = (
            ROOT / "docs" / "release-notes-v1.0.md"
        ).read_text(encoding="utf-8")

        self.assertIn("book-organize-v1.0-windows-x64.zip", notes)
        self.assertIn("--dry-run", notes)
        self.assertIn("uv sync", notes)
        self.assertIn("%LOCALAPPDATA%\\book-organize\\v1.0", notes)

    def test_third_party_notices_list_runtime_components(self):
        notices = (ROOT / "THIRD-PARTY-NOTICES.md").read_text(
            encoding="utf-8"
        )

        for expected in (
            "Python Software Foundation License Version 2",
            "SudachiPy 0.6.11",
            "SudachiDict-full 20260723",
            "Apache License 2.0",
            "`LEGAL`",
            "Nuitka 4.2.1",
        ):
            self.assertIn(expected, notices)


if __name__ == "__main__":
    unittest.main()
