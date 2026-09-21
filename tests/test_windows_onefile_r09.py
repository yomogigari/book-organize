"""v1.0-r09 のWindows onefileビルド機能を確認するテスト。"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "tools" / "windows-build"
BUILD_PY = BUILD_DIR / "build-windows-exe.py"
BUILD_PS1 = BUILD_DIR / "build-windows-exe.ps1"
BUILD_README = BUILD_DIR / "README.md"


class WindowsOnefileR09Test(unittest.TestCase):
    def test_build_python_has_valid_syntax(self):
        ast.parse(BUILD_PY.read_text(encoding="utf-8"))

    def test_powershell_exposes_onefile_mode(self):
        source = BUILD_PS1.read_text(encoding="utf-8-sig")
        self.assertIn('ValidateSet("standalone", "onefile")', source)
        self.assertIn("[string]$Mode", source)
        self.assertIn("'--mode'", source)

    def test_python_exposes_onefile_mode(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn('choices=("standalone", "onefile")', source)
        self.assertIn('f"--mode={mode}"', source)

    def test_onefile_uses_persistent_cache(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn('"--onefile-cache-mode=cached"', source)
        self.assertIn(
            'ONEFILE_CACHE_SPEC = "{CACHE_DIR}/book-organize/v1.0"',
            source,
        )

    def test_onefile_verifies_cached_dictionary(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn('cache_dir.rglob("system.dic")', source)
        self.assertIn("system.dic was not extracted into the onefile cache", source)

    def test_onefile_benchmarks_first_and_second_execution(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn("first_seconds", source)
        self.assertIn("second_seconds", source)
        self.assertIn("First list elapsed", source)
        self.assertIn("Second list elapsed", source)

    def test_build_readme_documents_onefile(self):
        readme = BUILD_README.read_text(encoding="utf-8")
        self.assertIn("-Mode onefile", readme)
        self.assertIn("{CACHE_DIR}/book-organize/v1.0", readme)
        self.assertIn("初回", readme)
        self.assertIn("2回目", readme)


if __name__ == "__main__":
    unittest.main()
