"""v1.0-r12 のWindows Release ZIP生成ツールを確認するテスト。"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "tools" / "release"
RELEASE_PY = RELEASE_DIR / "build-windows-release.py"
RELEASE_PS1 = RELEASE_DIR / "build-windows-release.ps1"
RELEASE_README = RELEASE_DIR / "README.md"
NOTICES = ROOT / "THIRD-PARTY-NOTICES.md"


class WindowsReleaseR12Test(unittest.TestCase):
    def test_release_tool_files_exist(self):
        for path in (
            RELEASE_PY,
            RELEASE_PS1,
            RELEASE_README,
        ):
            self.assertTrue(path.is_file(), path)

    def test_release_python_has_valid_syntax(self):
        ast.parse(RELEASE_PY.read_text(encoding="utf-8"))

    def test_release_asset_name_is_fixed(self):
        source = RELEASE_PY.read_text(encoding="utf-8")

        self.assertIn('VERSION = "1.0"', source)
        self.assertIn(
            'ASSET_FILENAME = f"{ASSET_BASENAME}.zip"',
            source,
        )
        self.assertIn(
            'ASSET_BASENAME = f"book-organize-v{VERSION}-windows-x64"',
            source,
        )

    def test_release_package_contains_required_documents(self):
        source = RELEASE_PY.read_text(encoding="utf-8")

        for expected in (
            '"book-organize.exe"',
            '"README.md"',
            '"CHANGELOG.md"',
            '"LICENSE"',
            '"THIRD-PARTY-NOTICES.md"',
            '"SHA256SUMS.txt"',
        ):
            self.assertIn(expected, source)

    def test_release_package_contains_third_party_license_files(self):
        source = RELEASE_PY.read_text(encoding="utf-8")

        for expected in (
            "Python-3.12-LICENSE.txt",
            "Apache-2.0.txt",
            "SudachiDict-full-LEGAL.txt",
            "LICENSE-2.0.txt",
            '"LEGAL"',
        ):
            self.assertIn(expected, source)

    def test_release_tool_verifies_checksums_and_zip_contents(self):
        source = RELEASE_PY.read_text(encoding="utf-8")

        self.assertIn("verify_checksum_file", source)
        self.assertIn("verify_release_zip", source)
        self.assertIn("sha256_file", source)
        self.assertIn("RELEASE BUILD RESULT: PASS", source)

    def test_release_zip_timestamp_does_not_require_iana_tzdata(self):
        source = RELEASE_PY.read_text(encoding="utf-8")

        self.assertNotIn("ZoneInfo", source)
        self.assertNotIn("Asia/Tokyo", source)
        self.assertIn("timezone(timedelta(hours=9))", source)

    def test_release_documentation_matches_artifacts(self):
        readme = RELEASE_README.read_text(encoding="utf-8")
        notices = NOTICES.read_text(encoding="utf-8")

        self.assertIn("book-organize-v1.0-windows-x64.zip", readme)
        self.assertIn("artifacts\\SHA256SUMS.txt", readme)

        for expected in (
            "Python-3.12-LICENSE.txt",
            "Apache-2.0.txt",
            "SudachiDict-full-LEGAL.txt",
        ):
            self.assertIn(expected, readme)
            self.assertIn(expected, notices)


if __name__ == "__main__":
    unittest.main()
