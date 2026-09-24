# book-organize

`book-organize` は、電子書籍ファイルのファイル名から作者名を抽出し、作者名の読みに基づいて整理用ディレクトリへ分類・移動する CLI ツールです。

作者名の読みには SudachiPy と SudachiDict-full を使用します。
SudachiPy の結果を補正したい場合は、作者名と読みを記述した簡易 CSV 辞書を指定できます。

## 主な機能

`book-organize` は、次の 3 つのサブコマンドを提供します。

- `run`: 分類情報を生成し、その結果を使ってファイルを移動する。
- `list`: ファイルを移動せず、分類情報を CSV または標準出力へ出力する。
- `move`: `list` で生成した既存 CSV に従ってファイルを移動する。

`run` と `move` は `--dry-run` に対応します。
実際にファイルを移動する前に、移動予定を確認できます。

## 対応環境

### Windows 版

Windows 向けの公開配布は、Nuitka の cached onefile 形式で作成した `book-organize.exe` です。
Python や uv を別にインストールせずに実行できます。

GitHub Release では、次の asset を配布します。

```text
book-organize-v1.0-windows-x64.zip
SHA256SUMS.txt
```

`SHA256SUMS.txt` には、公開 ZIP の SHA-256 を記録します。

onefile EXE は初回実行時に SudachiDict-full などの実行時データをユーザーキャッシュへ展開します。
v1.0 の展開先は通常、次のパスです。

```text
%LOCALAPPDATA%\book-organize\v1.0
```

v1.0 の検証ビルドでは、展開後のキャッシュ全体が約 377 MB になりました。
ビルド内容によって変わる可能性があるため、Windows 版を使用する場合は 400 MB 程度の空き容量を見込んでください。

### Python 版

Python 版の開発・実行環境は次のとおりです。

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- SudachiPy 0.6.11
- SudachiDict-full 20260723

依存関係は `pyproject.toml` と `uv.lock` で管理します。

```powershell
uv sync
```

## 最初の実行

最初にルートヘルプを確認します。
ルートヘルプには `run`、`list`、`move` の主要オプションも表示します。

```powershell
uv run book-organize.py -h
```

通常の整理では `run` を使用します。
最初は `--dry-run` を付け、移動予定だけを確認してください。

```powershell
uv run book-organize.py run --dir E:\E-book --dry-run
```

移動予定に問題がなければ、`--dry-run` を外して実行します。

```powershell
uv run book-organize.py run --dir E:\E-book
```

## ファイルを移動する前の確認

`run` と `move` は、対象の電子書籍ファイルを別のディレクトリへ移動します。
移動先を確認せずに実行しないでください。

元の配置へ戻す必要がある場合に備え、必要なファイルは実行前にバックアップしてください。

分類コードが `!!` のファイルは移動しません。
作者名を抽出できない場合や、読みを最後までカタカナとして取得できない場合に `!!` になります。

## サブコマンド

### `run`: 一覧生成と移動を続けて実行する

`run` は分類情報をメモリ上で生成し、その結果を使ってファイルを移動します。

```powershell
uv run book-organize.py run --dir E:\E-book --dry-run
```

分類情報を CSV にも保存する場合は `--out` を指定します。

```powershell
uv run book-organize.py run --dir E:\E-book --out book-list.csv --dry-run
```

### `list`: 分類情報だけを生成する

`list` はファイルを移動せず、分類情報を生成します。

```powershell
uv run book-organize.py list --dir E:\E-book --out book-list.csv
```

`--out` を指定しない場合は標準出力へ出力します。

```powershell
uv run book-organize.py list --dir E:\E-book
```

`--short` を指定すると、分類コードとファイル名の 2 列だけを出力します。

```powershell
uv run book-organize.py list --dir E:\E-book --short --out book-list.csv
```

### `move`: 既存 CSV に従って移動する

`move` は `list` で生成した CSV を読み込み、その内容に従ってファイルを移動します。

```powershell
uv run book-organize.py move --dir E:\E-book --csv book-list.csv --dry-run
```

移動予定に問題がなければ、`--dry-run` を外して実行します。

```powershell
uv run book-organize.py move --dir E:\E-book --csv book-list.csv
```

各サブコマンドのヘルプは個別にも確認できます。

```powershell
uv run book-organize.py run -h
uv run book-organize.py list -h
uv run book-organize.py move -h
```

## 簡易読み辞書

SudachiPy で期待した読みを取得できない作者名や、SudachiPy の結果より優先したい読みがある場合は、`--reading-dict` で簡易 CSV 辞書を指定できます。

辞書はヘッダーなしの 2 列 CSV です。
1 列目に作者名、2 列目に読みをカタカナで記述します。

```csv
サンプル作者,サンプルサクシャ
特殊な作者名,トクシュナサクシャメイ
```

UTF-8 と UTF-8 BOM 付き CSV を読み込めます。
空行は無視します。
同じ作者名を複数回登録した場合や、2 列以外の行がある場合はエラーになります。

既定のファイル名 `author-readings.csv` は、利用環境ごとの補正内容を保存するローカルファイルとして扱います。
このファイルは Git の管理対象には含めません。

作者名はファイル名から抽出した後に NFKC で正規化して比較します。
辞書に一致した作者名は、SudachiPy で解析せず辞書の読みを使用します。

```powershell
uv run book-organize.py list --dir E:\E-book --reading-dict author-readings.csv --out book-list.csv
```

`run` でも同じ辞書を使用できます。

```powershell
uv run book-organize.py run --dir E:\E-book --reading-dict author-readings.csv --dry-run
```

## 作者名の抽出規則

ファイル名に半角の `[` と `]` で囲まれた文字列がある場合、その最初の文字列を作者名として扱います。

```text
[サンプル作者] サンプル.epub
```

作者名に `×` が含まれる場合は、`×` より前だけを使用します。

```text
[サンプル作者×共同作者] サンプル.epub
```

この例では `サンプル作者` を作者名として扱います。

抽出した作者名は NFKC で正規化します。
作者名を抽出できない場合は分類コードを `!!` とします。

## 分類方法と移動先

作者名の読みをカタカナへ変換した後、濁音、半濁音、拗音、促音などを分類用に正規化します。
正規化した読みの先頭 2 文字を 50 音の行へ置き換え、2 文字の分類コードを生成します。

分類コードが `アカ` の場合、通常は次のディレクトリへ移動します。

```text
E:\E-book\ア行\アカ\
```

`--first-dir` を指定すると、1 階層目だけを使用します。

```powershell
uv run book-organize.py run --dir E:\E-book --first-dir --dry-run
```

この場合の移動先は次の形式です。

```text
E:\E-book\ア行\
```

## CSV の内容

通常の `list` は次の 6 列を出力します。

1. 分類コード
2. 正規化後の読みの先頭 2 文字
3. 分類用に正規化した読み
4. SudachiPy または簡易読み辞書から取得した読み
5. ファイル名から抽出した作者名
6. ファイル名

`--short` を指定した場合は、分類コードとファイル名の 2 列です。

分類コードが `!!` の行は、`run` と `move` で移動しません。

## 対応するファイル拡張子

現在は次の拡張子を分類対象とします。
大文字と小文字は区別しません。

```text
.zip .rar .7z .tar .gz .lzh .epub .mobi .pdf .azw3
```

## 開発者向け情報

全テストは次のコマンドで実行します。

```powershell
uv run python -m unittest discover -s tests -v
```

Windows EXE のビルドツールは `tools\windows-build` で管理します。
ビルドツールは Nuitka 4.2.1 を使用し、standalone と onefile の両方を検証できます。

```powershell
.\tools\windows-build\build-windows-exe.ps1
```

詳細は [tools/windows-build/README.md](tools/windows-build/README.md) を参照してください。

Windows 向け Release ZIP の生成ツールは `tools\release` で管理します。

```powershell
.\tools\release\build-windows-release.ps1
```

詳細は [tools/release/README.md](tools/release/README.md) を参照してください。

プロジェクト固有の開発契約は [docs/development/PROJECT-CONTRACT.md](docs/development/PROJECT-CONTRACT.md) を正本とします。
開発開始時の履歴資料は [docs/development-baseline.md](docs/development-baseline.md) に保持します。

## 使用ライブラリとライセンス

作者名の読みの取得には [SudachiPy](https://github.com/WorksApplications/SudachiPy) と [SudachiDict-full](https://pypi.org/project/SudachiDict-full/) を使用します。

`book-organize` 本体のライセンスは [LICENSE](LICENSE) を参照してください。

Windows 版に含まれる第三者ソフトウェアについては、[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) を参照してください。
公開用 ZIP には、再配布する第三者コンポーネントのライセンス本文も同梱します。
