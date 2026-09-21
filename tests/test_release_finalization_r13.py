"""v1.0-r13 の公開日確定を確認するテスト。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DATE = "2026-09-22"


class ReleaseFinalizationR13Test(unittest.TestCase):
    def test_changelog_has_release_date(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## v1.0 — {RELEASE_DATE}", text)
        self.assertNotIn("## v1.0 — Unreleased", text)

    def test_release_notes_have_release_date(self):
        text = (
            ROOT / "docs" / "release-notes-v1.0.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            f"# book-organize v1.0 Release Notes ({RELEASE_DATE})",
            text,
        )


if __name__ == "__main__":
    unittest.main()
