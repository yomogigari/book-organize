# Windows EXE ビルド

このディレクトリは、`book-organize` の Windows EXE を Nuitka と MinGW64 でビルドし、配布形式ごとの動作を検証するツールを管理します。

Nuitka は通常の実行時依存関係には追加しません。
ビルド時だけ `uv run --with` で Nuitka 4.2.1 を使用します。

## Packaging mode

ビルドツールは `standalone` と `onefile` を別の packaging mode として扱います。

### standalone

既定の mode は `standalone` です。
EXE 本体だけでなく、SudachiDict-full を含む配布ディレクトリ全体を検証対象とします。

```powershell
.\tools\windows-build\build-windows-exe.ps1
```

### onefile

GitHub Release の Windows 版は cached onefile を使用します。
onefile を検証する場合は `-Mode onefile` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile
```

onefile は実行時に内包ファイルを展開します。
`book-organize` では SudachiDict-full の辞書が大きいため、毎回展開して削除する方式ではなく、Nuitka の persistent cache を使用します。

v1.0 のキャッシュ指定は次のとおりです。

```text
{CACHE_DIR}/book-organize/v1.0
```

Windows では通常、ユーザーのローカルアプリケーションデータ配下へ展開されます。

## 開発中のオプション

未 commit の変更を含む開発中の検証だけ、`-AllowDirty` を指定できます。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile -AllowDirty
```

既存出力を削除して作り直す場合は `-CleanOutput` を指定します。

```powershell
.\tools\windows-build\build-windows-exe.ps1 -Mode onefile -CleanOutput
```

Release candidate の生成では、clean worktree から実行します。
`-AllowDirty` を Release candidate 生成の標準手順には使用しません。

## 出力先

既定の出力先は packaging mode ごとに分けます。

```text
work\book-organize-windows-standalone-output
work\book-organize-windows-onefile-output
```

ビルド出力は生成物であり、ソースコードの正本ではありません。

## ビルド時の検索パス

アプリケーション本体は `src\book_organize` にあります。
ビルドツールは Nuitka を起動する subprocess にだけ `PYTHONPATH=<repository>\src` を設定します。

さらに `--include-package=book_organize` を指定し、アプリケーション本体を配布物へ含めます。

## Sudachi の同梱

ビルド時には次のパッケージとデータを明示的に含めます。

- `sudachipy` package
- SudachiPy の package data と distribution metadata
- `sudachidict_full` package
- SudachiDict-full の package data と distribution metadata

SudachiDict-full の `resources\system.dic` は package data として含めます。

## 自動検証

ビルドツールは、対象リポジトリの HEAD と packaging mode を記録したうえで次を確認します。

- プロジェクトの全 `unittest`
- SudachiPy 0.6.11 と SudachiDict-full 20260723
- EXE の完全ヘルプ
- Python 版と EXE 版の `list` CSV の完全一致
- Python 版と EXE 版の `run --dry-run` 標準出力の完全一致

standalone では、配布ディレクトリ内の `system.dic` を確認します。

onefile では、既存キャッシュを削除してから初回の `list` を実行します。
展開された `system.dic` を確認した後、同じキャッシュを使って 2 回目の `list` を実行します。
初回と 2 回目の実行時間は `build-summary.txt` に記録します。

ビルド成功だけを Release 成功とは扱いません。
公開用 ZIP の生成と監査は [../release/README.md](../release/README.md) を参照してください。
