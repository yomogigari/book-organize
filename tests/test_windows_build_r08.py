"""v1.0-r08 のWindows EXEビルドツールを確認するテスト。"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "tools" / "windows-build"
BUILD_PY = BUILD_DIR / "build-windows-exe.py"
BUILD_PS1 = BUILD_DIR / "build-windows-exe.ps1"
BUILD_README = BUILD_DIR / "README.md"


class WindowsBuildR08Test(unittest.TestCase):
    def test_build_tool_files_exist(self):
        self.assertTrue(BUILD_PY.is_file())
        self.assertTrue(BUILD_PS1.is_file())
        self.assertTrue(BUILD_README.is_file())

    def test_build_python_has_valid_syntax(self):
        ast.parse(BUILD_PY.read_text(encoding="utf-8"))

    def test_build_tool_configures_src_pythonpath(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn('env["PYTHONPATH"]', source)
        self.assertIn('repo / "src"', source)
        self.assertIn('"--include-package=book_organize"', source)

    def test_build_tool_includes_sudachi_packages_and_dictionary_data(self):
        source = BUILD_PY.read_text(encoding="utf-8")

        for option in (
            '"--include-package=sudachipy"',
            '"--include-package-data=sudachipy"',
            '"--include-distribution-metadata=SudachiPy"',
            '"--include-package=sudachidict_full"',
            '"--include-package-data=sudachidict_full"',
            '"--include-distribution-metadata=SudachiDict-full"',
        ):
            self.assertIn(option, source)

        self.assertIn('rglob("system.dic")', source)

    def test_build_tool_pins_nuitka(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn('NUITKA_VERSION = "4.2.1"', source)

    def test_build_tool_verifies_python_and_exe_outputs(self):
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn("Python and EXE list CSV outputs are different", source)
        self.assertIn("Python and EXE run --dry-run stdout are different", source)

    def test_readme_documents_windows_build_tool(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("tools\\windows-build\\build-windows-exe.ps1", readme)
        self.assertIn("standalone", readme)
        self.assertIn("Nuitka", readme)


if __name__ == "__main__":
    unittest.main()
