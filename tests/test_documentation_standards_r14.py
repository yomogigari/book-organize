"""v1.0-r14 の開発標準採用と文書構成を確認するテスト。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "development" / "PROJECT-CONTRACT.md"

REWRITTEN_DOCS = (
    ROOT / "README.md",
    ROOT / "THIRD-PARTY-NOTICES.md",
    ROOT / "tools" / "windows-build" / "README.md",
    ROOT / "tools" / "release" / "README.md",
    CONTRACT,
)

PROHIBITED_EMPTY_PHRASES = (
    "重要なのは",
    "ここで押さえておきたい",
    "本質的に",
    "正面から",
    "多角的に",
    "深掘りする",
    "包括的に",
)


class DocumentationStandardsR14Test(unittest.TestCase):
    def test_project_contract_records_adopted_standards_snapshot(self):
        text = CONTRACT.read_text(encoding="utf-8")

        self.assertIn("Applied baseline: 共通の開発基準", text)
        self.assertIn("Adopted on: `2026-09-24`", text)
        self.assertNotIn("development-standards", text)
        self.assertIn("v1.0-r14", text)
        self.assertIn("次の公開 version へ更新した時点", text)
        self.assertIn("新しい公開 version の `r01`", text)
        self.assertNotIn("次の公開 version へ更新した後", text)
        self.assertNotIn("未 commit 論理変更", text)

    def test_project_contract_records_conditional_applicability(self):
        text = CONTRACT.read_text(encoding="utf-8")

        for expected in (
            "Generated artifacts | APPLY",
            "ローカル状態 / キャッシュ / output | APPLY",
            "設定 / Feature flag の段階展開 | N/A",
            "永続データストア / 復旧 | N/A",
            "Background jobs / resumability | N/A",
            "Network API / secrets | N/A",
            "プラグイン / 拡張機能 | N/A",
            "ソフトウェア更新 / ロールバック | N/A",
            "CI/CD / automation | N/A",
        ):
            self.assertIn(expected, text)

    def test_historical_documents_are_kept(self):
        self.assertTrue((ROOT / "docs" / "development-baseline.md").is_file())
        self.assertTrue((ROOT / "docs" / "release-notes-v1.0.md").is_file())

    def test_readme_is_user_facing_and_keeps_public_contracts(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for expected in (
            "## 主な機能",
            "## 対応環境",
            "## 最初の実行",
            "## ファイルを移動する前の確認",
            "## CSV の内容",
            "uv run book-organize.py run",
            "uv run book-organize.py list",
            "uv run book-organize.py move",
            "--reading-dict",
            "--dry-run",
            "book-organize-v1.0-windows-x64.zip",
            "%LOCALAPPDATA%\\book-organize\\v1.0",
            "SHA256SUMS.txt",
        ):
            self.assertIn(expected, text)

    def test_developer_details_are_linked_from_readme(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("tools/windows-build/README.md", text)
        self.assertIn("tools/release/README.md", text)
        self.assertIn("docs/development/PROJECT-CONTRACT.md", text)
        self.assertIn("docs/development-baseline.md", text)

    def test_rewritten_documents_have_single_h1_and_no_empty_phrases(self):
        for path in REWRITTEN_DOCS:
            text = path.read_text(encoding="utf-8")
            h1 = re.findall(r"(?m)^# (?!#).+$", text)
            self.assertEqual(1, len(h1), path)

            for phrase in PROHIBITED_EMPTY_PHRASES:
                self.assertNotIn(phrase, text, f"{path}: {phrase}")

            self.assertNotIn("Gitの", text, path)
            self.assertNotIn("2回目", text, path)

    def test_changelog_has_unreleased_documentation_entry(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("## Unreleased", text)
        self.assertIn("開発標準", text)
        self.assertIn("Project Contract", text)
        self.assertIn("v1.0 — 2026-09-22", text)


if __name__ == "__main__":
    unittest.main()
