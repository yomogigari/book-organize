# Windows EXEビルド

`book-organize` のWindows standalone EXEは、NuitkaとMinGW64を使用してビルドします。

ビルドツールはこのリポジトリ内で管理します。Nuitkaは通常の実行時依存関係には追加せず、ビルド時だけ `uv run --with` でNuitka 4.2.1を使用します。

## 実行方法

リポジトリルートから次のコマンドを実行します。

```powershell
.\tools\windows-build\build-windows-exe.ps1
```

開発中でworktreeに未commit変更がある場合だけ、次のオプションを指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -AllowDirty
```

既定の出力先は、リポジトリの親ディレクトリにある `work\book-organize-windows-build-output` です。

既存出力を削除して作り直す場合は `-CleanOutput` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -CleanOutput
```

## ビルド時の検索パス

本体は `src\book_organize` にあるため、ビルドツールはNuitkaを起動するsubprocessにだけ `PYTHONPATH=<repository>\src` を設定します。

さらに `--include-package=book_organize` を明示し、アプリ本体をstandalone配布物へ含めます。

## Sudachiの同梱

ビルド時には次を明示的に含めます。

- `sudachipy` package
- SudachiPyのpackage dataとdistribution metadata
- `sudachidict_full` package
- SudachiDict-fullのpackage dataとdistribution metadata

SudachiDict-fullの `resources\system.dic` はpackage dataとして配布物へ含めます。

## 自動検証

ビルドツールは次の検証も行います。

- プロジェクトの全unittest
- SudachiPy 0.6.11 / SudachiDict-full 20260723の確認
- standalone配布物内の `system.dic` 確認
- EXEの完全ヘルプ確認
- Python版とEXE版の `list` CSV完全一致
- Python版とEXE版の `run --dry-run` 標準出力完全一致

最初にstandalone形式で検証します。onefile化はstandaloneで動作確認した後に検討します。
