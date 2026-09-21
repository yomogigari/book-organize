from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


VERSION = "1.0"
ASSET_BASENAME = f"book-organize-v{VERSION}-windows-x64"
ASSET_FILENAME = f"{ASSET_BASENAME}.zip"
PACKAGE_DIRNAME = ASSET_BASENAME

REQUIRED_PACKAGE_FILES = (
    "book-organize.exe",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "THIRD-PARTY-NOTICES.md",
    "SHA256SUMS.txt",
    "third-party-licenses/Python-3.12-LICENSE.txt",
    "third-party-licenses/Apache-2.0.txt",
    "third-party-licenses/SudachiDict-full-LEGAL.txt",
)


def run(
    args: list[str],
    *,
    cwd: Path,
    capture: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    """外部コマンドを実行し、失敗時は終了コード付きで停止する。"""
    print("+", subprocess.list2cmdline(args))
    proc = subprocess.run(
        args,
        cwd=cwd,
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


def git_text(repo: Path, *args: str) -> str:
    proc = run(["git", *args], cwd=repo, capture=True)
    return proc.stdout.decode("utf-8", errors="replace")


def find_repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parents[2]


def assert_repository(repo: Path, *, allow_dirty: bool) -> str:
    if platform.system() != "Windows":
        raise RuntimeError("ERROR Windowsで実行してください。")

    required = (
        repo / ".git",
        repo / "book-organize.py",
        repo / "README.md",
        repo / "CHANGELOG.md",
        repo / "LICENSE",
        repo / "THIRD-PARTY-NOTICES.md",
        repo / "tools" / "windows-build" / "build-windows-exe.py",
    )
    for path in required:
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

    return head


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def run_project_tests(repo: Path) -> None:
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


def build_onefile(
    repo: Path,
    build_output: Path,
    *,
    allow_dirty: bool,
) -> Path:
    builder = repo / "tools" / "windows-build" / "build-windows-exe.py"

    args = [
        sys.executable,
        str(builder),
        "--repo-root",
        str(repo),
        "--output-root",
        str(build_output),
        "--mode",
        "onefile",
        "--clean-output",
    ]
    if allow_dirty:
        args.append("--allow-dirty")

    run(args, cwd=repo)

    exe = build_output / "nuitka" / "book-organize.exe"
    summary = build_output / "build-summary.txt"

    if not exe.is_file():
        raise RuntimeError(f"ERROR onefile EXE not found: {exe}")
    if not summary.is_file():
        raise RuntimeError(f"ERROR build summary not found: {summary}")

    summary_text = summary.read_text(encoding="utf-8")
    for required in (
        "EXE help: PASS",
        "Python list CSV == EXE list CSV: PASS",
        "Python run --dry-run stdout == EXE run --dry-run stdout: PASS",
    ):
        if required not in summary_text:
            raise RuntimeError(
                f"ERROR onefile build summary does not contain: {required}"
            )

    return exe


def locate_runtime_license_sources(repo: Path) -> dict[str, Path]:
    """プロジェクト実行環境から再配布ライセンスの元ファイルを特定する。"""
    code = "\n".join(
        [
            "import json",
            "import sys",
            "from pathlib import Path",
            "import sudachidict_full",
            "",
            "dict_root = Path(sudachidict_full.__file__).resolve().parent",
            "print(json.dumps({",
            "    'python_base': str(Path(sys.base_prefix).resolve()),",
            "    'dict_root': str(dict_root),",
            "}, ensure_ascii=False))",
        ]
    )

    proc = run(
        ["uv", "run", "python", "-c", code],
        cwd=repo,
        capture=True,
    )
    values = json.loads(proc.stdout.decode("utf-8"))

    python_base = Path(values["python_base"])
    dict_root = Path(values["dict_root"])

    python_candidates = (
        python_base / "LICENSE.txt",
        python_base / "LICENSE",
    )
    python_license = next(
        (path for path in python_candidates if path.is_file()),
        None,
    )
    if python_license is None:
        tried = "\n".join(f"  {path}" for path in python_candidates)
        raise RuntimeError(
            "ERROR CPython license file not found. Tried:\n" + tried
        )

    apache_license = dict_root / "resources" / "LICENSE-2.0.txt"
    sudachi_legal = dict_root / "resources" / "LEGAL"

    for path in (apache_license, sudachi_legal):
        if not path.is_file():
            raise RuntimeError(
                f"ERROR SudachiDict-full license resource not found: {path}"
            )

    return {
        "python": python_license,
        "apache": apache_license,
        "sudachi_legal": sudachi_legal,
    }


def prepare_staging(
    repo: Path,
    staging_root: Path,
    exe: Path,
    license_sources: dict[str, Path],
) -> Path:
    package = staging_root / PACKAGE_DIRNAME
    package.mkdir(parents=True)

    shutil.copy2(exe, package / "book-organize.exe")

    for name in (
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "THIRD-PARTY-NOTICES.md",
    ):
        shutil.copy2(repo / name, package / name)

    third_party = package / "third-party-licenses"
    third_party.mkdir()

    shutil.copy2(
        license_sources["python"],
        third_party / "Python-3.12-LICENSE.txt",
    )
    shutil.copy2(
        license_sources["apache"],
        third_party / "Apache-2.0.txt",
    )
    shutil.copy2(
        license_sources["sudachi_legal"],
        third_party / "SudachiDict-full-LEGAL.txt",
    )

    return package


def write_package_checksums(package: Path) -> Path:
    checksum_path = package / "SHA256SUMS.txt"
    lines: list[str] = []

    for path in sorted(package.rglob("*")):
        if not path.is_file() or path == checksum_path:
            continue

        rel = path.relative_to(package).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}")

    checksum_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return checksum_path


def verify_package_tree(package: Path) -> None:
    actual = sorted(
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file()
    )
    expected = sorted(REQUIRED_PACKAGE_FILES)

    if actual != expected:
        print("Expected package files:")
        for item in expected:
            print(f"  {item}")
        print("Actual package files:")
        for item in actual:
            print(f"  {item}")
        raise RuntimeError("ERROR unexpected release package contents.")

    forbidden_parts = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".venv",
    }
    for path in package.rglob("*"):
        if any(part in forbidden_parts for part in path.parts):
            raise RuntimeError(
                f"ERROR forbidden generated path in release package: {path}"
            )

    for path in package.rglob("*"):
        if path.is_file() and path.stat().st_size <= 0:
            raise RuntimeError(f"ERROR empty release file: {path}")


def verify_checksum_file(package: Path) -> None:
    checksum_path = package / "SHA256SUMS.txt"
    entries: dict[str, str] = {}

    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest

    expected_files = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path != checksum_path
    }
    if set(entries) != expected_files:
        raise RuntimeError(
            "ERROR package SHA256SUMS file list does not match package contents."
        )

    for rel, expected_hash in entries.items():
        actual_hash = sha256_file(package / rel)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"ERROR package checksum mismatch: {rel}"
            )


def make_release_zip(
    package: Path,
    artifacts_dir: Path,
) -> Path:
    artifacts_dir.mkdir(parents=True)
    zip_path = artifacts_dir / ASSET_FILENAME

    # 日本標準時はUTC+09:00で固定されているため、IANA tzdataには依存しない。
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    zip_dt = (
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second - now.second % 2,
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        allowZip64=True,
    ) as archive:
        top = zipfile.ZipInfo(f"{PACKAGE_DIRNAME}/")
        top.date_time = zip_dt
        top.external_attr = (0o40755 << 16) | 0x10
        archive.writestr(top, b"")

        for path in sorted(package.rglob("*")):
            if not path.is_file():
                continue

            rel = path.relative_to(package).as_posix()
            info = zipfile.ZipInfo(f"{PACKAGE_DIRNAME}/{rel}")
            info.date_time = zip_dt
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    return zip_path


def verify_release_zip(zip_path: Path) -> None:
    prefix = f"{PACKAGE_DIRNAME}/"
    expected = {
        prefix + rel
        for rel in REQUIRED_PACKAGE_FILES
    }

    with zipfile.ZipFile(zip_path) as archive:
        actual = {
            info.filename
            for info in archive.infolist()
            if not info.is_dir()
        }
        if actual != expected:
            print("Expected ZIP files:")
            for item in sorted(expected):
                print(f"  {item}")
            print("Actual ZIP files:")
            for item in sorted(actual):
                print(f"  {item}")
            raise RuntimeError("ERROR unexpected ZIP contents.")

        checksum_text = archive.read(
            prefix + "SHA256SUMS.txt"
        ).decode("utf-8")

        checksum_entries: dict[str, str] = {}
        for line in checksum_text.splitlines():
            if not line:
                continue
            digest, rel = line.split("  ", 1)
            checksum_entries[rel] = digest

        for rel, expected_hash in checksum_entries.items():
            data = archive.read(prefix + rel)
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != expected_hash:
                raise RuntimeError(
                    f"ERROR checksum mismatch inside ZIP: {rel}"
                )


def write_artifact_checksum(
    artifacts_dir: Path,
    zip_path: Path,
) -> Path:
    path = artifacts_dir / "SHA256SUMS.txt"
    path.write_text(
        f"{sha256_file(zip_path)}  {zip_path.name}\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="book-organize v1.0 Windows Release ZIPを生成します。"
    )
    parser.add_argument("--repo-root")
    parser.add_argument("--output-root")
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    repo = find_repo_root(args.repo_root)
    head = assert_repository(repo, allow_dirty=args.allow_dirty)

    output_root = (
        Path(args.output_root).resolve()
        if args.output_root
        else repo.parent / "work" / "book-organize-v1.0-release-output"
    )

    if output_root.exists():
        if not args.clean_output:
            raise RuntimeError(
                f"ERROR output directory already exists: {output_root}\n"
                "-CleanOutput または --clean-output を指定してください。"
            )
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True)
    build_output = output_root / "_build"
    staging_root = output_root / "_staging"
    artifacts_dir = output_root / "artifacts"

    print(f"Output: {output_root}")

    try:
        print("\n[1/8] Project tests")
        run_project_tests(repo)

        print("\n[2/8] Onefile build and verification")
        exe = build_onefile(
            repo,
            build_output,
            allow_dirty=args.allow_dirty,
        )

        print("\n[3/8] Locate license sources")
        license_sources = locate_runtime_license_sources(repo)
        for name, path in license_sources.items():
            print(f"{name}: {path}")

        print("\n[4/8] Prepare staging package")
        package = prepare_staging(
            repo,
            staging_root,
            exe,
            license_sources,
        )
        write_package_checksums(package)
        verify_package_tree(package)
        verify_checksum_file(package)

        print("\n[5/8] Verify packaged EXE")
        run([str(package / "book-organize.exe"), "-h"], cwd=package)

        print("\n[6/8] Create Release ZIP")
        zip_path = make_release_zip(package, artifacts_dir)
        verify_release_zip(zip_path)

        print("\n[7/8] Create external checksum")
        external_checksums = write_artifact_checksum(
            artifacts_dir,
            zip_path,
        )

        print("\n[8/8] Summary")
        summary = (
            "book-organize v1.0 Windows release\n"
            "==================================\n"
            f"Repository HEAD: {head}\n"
            f"Asset: {zip_path}\n"
            f"Asset SHA-256: {sha256_file(zip_path)}\n"
            f"Asset size: {zip_path.stat().st_size}\n"
            f"EXE SHA-256: {sha256_file(package / 'book-organize.exe')}\n"
            f"EXE size: {(package / 'book-organize.exe').stat().st_size}\n"
            f"External checksums: {external_checksums}\n"
            "\n"
            "Verification\n"
            "------------\n"
            "Project tests: PASS\n"
            "Onefile build verification: PASS\n"
            "Package file list: PASS\n"
            "Package SHA256SUMS: PASS\n"
            "Packaged EXE help: PASS\n"
            "Release ZIP contents: PASS\n"
            "Release ZIP internal checksums: PASS\n"
        )

        summary_path = output_root / "release-summary.txt"
        summary_path.write_text(
            summary,
            encoding="utf-8",
            newline="\n",
        )

        print(summary)
        print(f"Summary: {summary_path}")
        print("RELEASE BUILD RESULT: PASS")
        return 0
    except Exception:
        print(
            f"\nRELEASE BUILD RESULT: FAIL\n"
            f"Diagnostic files remain in: {output_root}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
