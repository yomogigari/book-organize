# Windows EXEビルド

`book-organize` のWindows EXEは、NuitkaとMinGW64を使用してビルドします。

ビルドツールはこのリポジトリ内で管理します。Nuitkaは通常の実行時依存関係には追加せず、ビルド時だけ `uv run --with` でNuitka 4.2.1を使用します。

## standalone

既定値はstandaloneです。

```powershell
.\tools\windows-build\build-windows-exe.ps1
```

standaloneでは、EXE本体とSudachiDict-fullを含む配布ディレクトリを生成します。

## onefile

onefileを検証する場合は `-Mode onefile` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile
```

onefileは実行時に内包ファイルを展開します。`book-organize` ではSudachiDict-fullの辞書が大きいため、毎回一時展開して削除する方式ではなく、Nuitkaのcached onefileを使用します。

展開先は次です。

```text
{CACHE_DIR}/book-organize/v1.0
```

Windowsでは通常、ユーザーのローカルアプリケーションデータ配下へ展開されます。

ビルド後の自動検証では、既存キャッシュを削除してから1回目の `list` を実行し、展開された `system.dic` を確認します。その後、同じキャッシュを使って2回目の `list` を実行し、両方の実行時間を `build-summary.txt` に記録します。

## 共通オプション

開発中でworktreeに未commit変更がある場合だけ、`-AllowDirty` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile -AllowDirty
```

既存出力を削除して作り直す場合は `-CleanOutput` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile -CleanOutput
```

既定の出力先は形式ごとに分かれます。

```text
work\book-organize-windows-standalone-output
work\book-organize-windows-onefile-output
```

## ビルド時の検索パス

本体は `src\book_organize` にあるため、ビルドツールはNuitkaを起動するsubprocessにだけ `PYTHONPATH=<repository>\src` を設定します。

さらに `--include-package=book_organize` を明示し、アプリ本体を配布物へ含めます。

## Sudachiの同梱

ビルド時には次を明示的に含めます。

- `sudachipy` package
- SudachiPyのpackage dataとdistribution metadata
- `sudachidict_full` package
- SudachiDict-fullのpackage dataとdistribution metadata

SudachiDict-fullの `resources\system.dic` はpackage dataとして含めます。

## 自動検証

ビルドツールは次を確認します。

- プロジェクトの全unittest
- SudachiPy 0.6.11 / SudachiDict-full 20260723
- EXEの完全ヘルプ
- Python版とEXE版の `list` CSV完全一致
- Python版とEXE版の `run --dry-run` 標準出力完全一致

standaloneでは配布ディレクトリ内の `system.dic` を確認します。

onefileでは初回実行後のキャッシュ内 `system.dic` を確認し、初回と2回目の `list` 実行時間も記録します。
