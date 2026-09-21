from __future__ import annotations

import argparse
import hashlib
import locale
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


NUITKA_VERSION = "4.2.1"


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    """外部コマンドを実行し、失敗時は終了コード付きで停止する。"""
    print("+", subprocess.list2cmdline(args))
    proc = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if proc.returncode != 0:
        if capture:
            if proc.stdout:
                sys.stdout.buffer.write(proc.stdout)
            if proc.stderr:
                sys.stderr.buffer.write(proc.stderr)
        raise RuntimeError(
            f"ERROR command failed with exit code {proc.returncode}: "
            + subprocess.list2cmdline(args)
        )
    return proc


def decode_output(data: bytes) -> str:
    """Windows上の外部コマンド出力を診断表示用に文字列化する。"""
    candidates = ("utf-8", locale.getpreferredencoding(False), "cp932")
    seen: set[str] = set()
    for encoding in candidates:
        if not encoding:
            continue
        key = encoding.lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    return data.decode("utf-8", errors="replace")


def git_text(repo: Path, *args: str) -> str:
    proc = run(["git", *args], cwd=repo, capture=True)
    return proc.stdout.decode("utf-8", errors="replace")


def find_repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()

    # tools/windows-build/build-windows-exe.py からリポジトリルートを求める。
    return Path(__file__).resolve().parents[2]


def assert_repository(repo: Path, *, allow_dirty: bool) -> None:
    if platform.system() != "Windows":
        raise RuntimeError("ERROR Windowsで実行してください。")

    for path in (
        repo / ".git",
        repo / "book-organize.py",
        repo / "src" / "book_organize",
        repo / "pyproject.toml",
        repo / "uv.lock",
    ):
        if not path.exists():
            raise RuntimeError(f"ERROR required path not found: {path}")

    head = git_text(repo, "rev-parse", "HEAD").strip()
    print(f"Repository HEAD: {head}")

    status = git_text(repo, "status", "--porcelain")
    if status.strip():
        if allow_dirty:
            print("Worktree: dirty (--allow-dirty)")
        else:
            print(status, end="")
            raise RuntimeError(
                "ERROR worktree is not clean. "
                "開発中の検証だけ --allow-dirty を使用してください。"
            )
    else:
        print("Worktree: clean")


def inspect_sudachi(repo: Path) -> str:
    code = "\n".join(
        [
            "from pathlib import Path",
            "import importlib.metadata",
            "import sudachidict_full",
            "import sudachipy",
            "import sys",
            "",
            "dict_root = Path(sudachidict_full.__file__).resolve().parent",
            "system_dic = dict_root / 'resources' / 'system.dic'",
            "",
            "print('python=' + sys.version.replace(chr(10), ' '))",
            "print('sudachipy=' + importlib.metadata.version('SudachiPy'))",
            "print('sudachidict-full=' + importlib.metadata.version('SudachiDict-full'))",
            "print('system_dic=' + str(system_dic))",
            "print('system_dic_exists=' + str(system_dic.is_file()))",
            "print('system_dic_size=' + str(system_dic.stat().st_size if system_dic.is_file() else -1))",
        ]
    )
    proc = run(["uv", "run", "python", "-c", code], cwd=repo, capture=True)
    text = decode_output(proc.stdout)
    print(text, end="" if text.endswith("\n") else "\n")

    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    if values.get("sudachipy") != "0.6.11":
        raise RuntimeError(
            "ERROR unexpected SudachiPy version: "
            + values.get("sudachipy", "<missing>")
        )
    if values.get("sudachidict-full") != "20260723":
        raise RuntimeError(
            "ERROR unexpected SudachiDict-full version: "
            + values.get("sudachidict-full", "<missing>")
        )
    if values.get("system_dic_exists") != "True":
        raise RuntimeError("ERROR SudachiDict-full system.dic not found.")

    return text


def make_build_env(repo: Path) -> dict[str, str]:
    """Nuitkaがsrcレイアウトを解決できるようコンパイル時PYTHONPATHを設定する。"""
    env = os.environ.copy()
    src = str(repo / "src")
    previous = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not previous else src + os.pathsep + previous
    print(f"Build PYTHONPATH: {src}")
    return env


def make_sample_input(output_root: Path) -> tuple[Path, Path]:
    sample_dir = output_root / "verification" / "sample-input"
    sample_dir.mkdir(parents=True)

    for name in (
        "[香月美夜] 本好きサンプル.epub",
        "[大沼隆揮] 読み補正サンプル.epub",
        "(一般コミック) [蓬がり×よもーぎ] サンプル.zip",
    ):
        (sample_dir / name).write_bytes(b"")

    reading_dict = output_root / "verification" / "author-readings.csv"
    reading_dict.write_text(
        "大沼隆揮,オオヌマタカシキ\n"
        "蓬がり,ヨモギガリ\n",
        encoding="utf-8",
        newline="\n",
    )
    return sample_dir, reading_dict


def python_baseline(
    repo: Path,
    output_root: Path,
    sample_dir: Path,
    reading_dict: Path,
) -> tuple[Path, bytes]:
    csv_path = output_root / "verification" / "python-list.csv"
    run(
        [
            "uv",
            "run",
            "book-organize.py",
            "list",
            "--dir",
            str(sample_dir),
            "--reading-dict",
            str(reading_dict),
            "--out",
            str(csv_path),
        ],
        cwd=repo,
    )

    proc = run(
        [
            "uv",
            "run",
            "book-organize.py",
            "run",
            "--dir",
            str(sample_dir),
            "--reading-dict",
            str(reading_dict),
            "--dry-run",
        ],
        cwd=repo,
        capture=True,
    )
    (output_root / "verification" / "python-run.stdout.log").write_bytes(proc.stdout)
    (output_root / "verification" / "python-run.stderr.log").write_bytes(proc.stderr)
    return csv_path, proc.stdout


def build_standalone(repo: Path, output_root: Path) -> Path:
    build_root = output_root / "nuitka"
    build_root.mkdir(parents=True)
    report = output_root / "nuitka-report.xml"

    env = make_build_env(repo)
    command = [
        "uv",
        "run",
        "--with",
        f"nuitka=={NUITKA_VERSION}",
        "python",
        "-m",
        "nuitka",
        "--mode=standalone",
        "--mingw64",
        "--assume-yes-for-downloads",
        f"--output-dir={build_root}",
        "--output-filename=book-organize.exe",
        "--include-package=book_organize",
        "--include-package=sudachipy",
        "--include-package-data=sudachipy",
        "--include-distribution-metadata=SudachiPy",
        "--include-package=sudachidict_full",
        "--include-package-data=sudachidict_full",
        "--include-distribution-metadata=SudachiDict-full",
        f"--report={report}",
        str(repo / "book-organize.py"),
    ]
    run(command, cwd=repo, env=env)

    candidates = [
        path
        for path in build_root.rglob("book-organize.exe")
        if path.parent.name.endswith(".dist")
    ]
    if len(candidates) != 1:
        found = "\n".join(f"  {path}" for path in candidates) or "  <none>"
        raise RuntimeError(
            "ERROR expected exactly one standalone executable, found:\n" + found
        )

    exe = candidates[0]
    print(f"Standalone EXE: {exe}")
    return exe


def verify_dictionary(exe: Path) -> Path:
    candidates = list(exe.parent.rglob("system.dic"))
    if not candidates:
        raise RuntimeError(
            "ERROR system.dic was not included in the standalone distribution."
        )

    preferred = [
        path for path in candidates
        if "sudachidict_full" in str(path).lower()
    ]
    system_dic = preferred[0] if preferred else candidates[0]

    if system_dic.stat().st_size <= 0:
        raise RuntimeError("ERROR included system.dic is empty.")

    print(
        f"Included dictionary: {system_dic} "
        f"({system_dic.stat().st_size:,} bytes)"
    )
    return system_dic


def verify_executable(
    repo: Path,
    output_root: Path,
    exe: Path,
    sample_dir: Path,
    reading_dict: Path,
    python_csv: Path,
    python_run_stdout: bytes,
) -> str:
    verification = output_root / "verification"

    help_proc = run([str(exe), "-h"], cwd=repo, capture=True)
    (verification / "exe-help.stdout.log").write_bytes(help_proc.stdout)
    (verification / "exe-help.stderr.log").write_bytes(help_proc.stderr)

    for token in (b"--dry-run", b"--reading-dict", b"--first-dir", b"--csv"):
        if token not in help_proc.stdout:
            raise RuntimeError(
                f"ERROR EXE help does not contain {token.decode('ascii')}."
            )

    exe_csv = verification / "exe-list.csv"
    run(
        [
            str(exe),
            "list",
            "--dir",
            str(sample_dir),
            "--reading-dict",
            str(reading_dict),
            "--out",
            str(exe_csv),
        ],
        cwd=repo,
    )

    if python_csv.read_bytes() != exe_csv.read_bytes():
        raise RuntimeError("ERROR Python and EXE list CSV outputs are different.")

    run_proc = run(
        [
            str(exe),
            "run",
            "--dir",
            str(sample_dir),
            "--reading-dict",
            str(reading_dict),
            "--dry-run",
        ],
        cwd=repo,
        capture=True,
    )
    (verification / "exe-run.stdout.log").write_bytes(run_proc.stdout)
    (verification / "exe-run.stderr.log").write_bytes(run_proc.stderr)

    if python_run_stdout != run_proc.stdout:
        raise RuntimeError(
            "ERROR Python and EXE run --dry-run stdout are different."
        )

    return hashlib.sha256(exe.read_bytes()).hexdigest()


def directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="book-organize Windows standalone EXEをビルドして検証します。"
    )
    parser.add_argument("--repo-root")
    parser.add_argument("--output-root")
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    repo = find_repo_root(args.repo_root)
    assert_repository(repo, allow_dirty=args.allow_dirty)

    output_root = (
        Path(args.output_root).resolve()
        if args.output_root
        else repo.parent / "work" / "book-organize-windows-build-output"
    )

    if output_root.exists():
        if not args.clean_output:
            raise RuntimeError(
                f"ERROR output directory already exists: {output_root}\n"
                "--clean-output を指定して作り直してください。"
            )
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True)
    print(f"Output: {output_root}")

    try:
        print("\n[1/7] Project tests")
        run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            cwd=repo,
        )

        print("\n[2/7] Sudachi environment")
        sudachi_report = inspect_sudachi(repo)

        print("\n[3/7] Python baseline")
        sample_dir, reading_dict = make_sample_input(output_root)
        python_csv, python_stdout = python_baseline(
            repo, output_root, sample_dir, reading_dict
        )

        print("\n[4/7] Nuitka standalone build")
        exe = build_standalone(repo, output_root)

        print("\n[5/7] Dictionary verification")
        system_dic = verify_dictionary(exe)

        print("\n[6/7] EXE behavior verification")
        exe_sha = verify_executable(
            repo,
            output_root,
            exe,
            sample_dir,
            reading_dict,
            python_csv,
            python_stdout,
        )

        print("\n[7/7] Summary")
        summary = (
            "book-organize Windows standalone build\n"
            "=====================================\n"
            f"Nuitka: {NUITKA_VERSION}\n"
            f"Repository HEAD: {git_text(repo, 'rev-parse', 'HEAD').strip()}\n"
            f"Platform: {platform.platform()}\n"
            "\n"
            "Sudachi environment\n"
            "-------------------\n"
            f"{sudachi_report.rstrip()}\n"
            "\n"
            "Standalone\n"
            "----------\n"
            f"EXE: {exe}\n"
            f"EXE SHA-256: {exe_sha}\n"
            f"EXE size: {exe.stat().st_size}\n"
            f"Distribution size: {directory_size(exe.parent)}\n"
            f"system.dic: {system_dic}\n"
            f"system.dic size: {system_dic.stat().st_size}\n"
            "\n"
            "Verification\n"
            "------------\n"
            "Project tests: PASS\n"
            "EXE help: PASS\n"
            "Python list CSV == EXE list CSV: PASS\n"
            "Python run --dry-run stdout == EXE run --dry-run stdout: PASS\n"
        )
        summary_path = output_root / "build-summary.txt"
        summary_path.write_text(summary, encoding="utf-8", newline="\n")

        print(summary)
        print(f"Summary: {summary_path}")
        print("BUILD RESULT: PASS")
        return 0
    except Exception:
        print(
            f"\nBUILD RESULT: FAIL\nDiagnostic files remain in: {output_root}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
