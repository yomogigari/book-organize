"""v1.0-r07 のローカル読み辞書管理を確認するテスト。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LocalReadingDictionaryR07Test(unittest.TestCase):
    def test_default_reading_dictionary_is_gitignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("author-readings.csv", gitignore)

    def test_readme_documents_local_dictionary_handling(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("author-readings.csv", readme)
        self.assertIn("Gitの管理対象には含めません", readme)


if __name__ == "__main__":
    unittest.main()
