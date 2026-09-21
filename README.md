# book-organize

`book-organize` は、電子書籍ファイルのファイル名から作者名を抽出し、作者名の読みに基づいて整理用ディレクトリへ移動するCLIツールです。

作者名の読みは SudachiPy と SudachiDict-full で取得します。SudachiPyの結果を補正したい場合は、作者名と読みを記述した簡易CSV辞書を指定できます。

## 動作環境

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- SudachiPy 0.6.11
- SudachiDict-full 20260723

依存関係は `pyproject.toml` と `uv.lock` で管理しています。

```powershell
uv sync
```

## ファイルを移動する前の確認

`run` と `move` は電子書籍ファイルを別のディレクトリへ移動します。最初に `--dry-run` を指定し、移動先を確認してください。

ファイルのバックアップが必要な場合は、実際の移動を行う前に作成してください。

## 基本的な使い方

ヘルプは次のコマンドで確認できます。

```powershell
uv run book-organize.py -h
```

統合CLIには `run`、`list`、`move` の3つのサブコマンドがあります。

### 一覧生成と移動を続けて実行する

通常は `run` を使用します。最初に `--dry-run` で移動予定を確認します。

```powershell
uv run book-organize.py run --dir E:\E-book --dry-run
```

内容に問題がなければ、`--dry-run` を外して実行します。

```powershell
uv run book-organize.py run --dir E:\E-book
```

生成した分類情報をCSVにも保存する場合は `--out` を指定します。

```powershell
uv run book-organize.py run --dir E:\E-book --out book-list.csv --dry-run
```

### 分類用CSVだけを生成する

`list` はファイルを移動せず、分類情報を生成します。

```powershell
uv run book-organize.py list --dir E:\E-book --out book-list.csv
```

`--out` を指定しない場合は標準出力へ出力します。

```powershell
uv run book-organize.py list --dir E:\E-book
```

`--short` を指定すると、移動先の分類コードとファイル名だけを出力します。

```powershell
uv run book-organize.py list --dir E:\E-book --short --out book-list.csv
```

### 既存のCSVに従って移動する

`move` は `list` で生成したCSVを読み込み、ファイルを移動します。

```powershell
uv run book-organize.py move --dir E:\E-book --csv book-list.csv --dry-run
```

移動予定に問題がなければ、`--dry-run` を外します。

```powershell
uv run book-organize.py move --dir E:\E-book --csv book-list.csv
```

## 簡易読み辞書

SudachiPyで期待した読みを取得できない作者名や、SudachiPyの結果より優先したい読みがある場合は、`--reading-dict` で簡易CSV辞書を指定できます。

辞書はヘッダーなしの2列CSVです。1列目に作者名、2列目に読みをカタカナで記述します。

```csv
蓬がり,ヨモギガリ
特殊な作者名,トクシュナサクシャメイ
```

UTF-8とUTF-8 BOM付きCSVを読み込めます。空行は無視します。同じ作者名を複数回登録した場合や、2列以外の行がある場合はエラーになります。

作者名はファイル名から抽出した後にNFKCで正規化して比較します。辞書に一致した作者名は、SudachiPyで解析せず辞書の読みを使用します。

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
[蓬がり] サンプル.epub
```

作者名に `×` が含まれる場合は、`×` より前だけを使用します。

```text
[蓬がり×よもーぎ] サンプル.epub
```

この場合、作者名は `蓬がり` です。

抽出した作者名はNFKCで正規化します。作者名を抽出できない場合は分類コードを `!!` とし、移動対象から除外します。

## 分類方法

作者名の読みをカタカナへ変換した後、濁音・半濁音・拗音・促音などを分類用に正規化します。先頭2文字を50音の行へ置き換えた2文字を分類コードとして使用します。

たとえば分類コードが `アカ` の場合、通常は次のディレクトリへ移動します。

```text
E:\E-book\ア行\アカ\
```

`--first-dir` を指定すると、1階層目だけを使用します。

```powershell
uv run book-organize.py run --dir E:\E-book --first-dir --dry-run
```

この場合の移動先は次の形式です。

```text
E:\E-book\ア行\
```

## CSVの内容

通常の `list` は次の6列を出力します。

1. 分類コード
2. 正規化後の読みの先頭2文字
3. 分類用に正規化した読み
4. SudachiPyまたは簡易読み辞書から取得した読み
5. ファイル名から抽出した作者名
6. ファイル名

`--short` を指定した場合は、分類コードとファイル名の2列です。

分類コードが `!!` の行は、`run` と `move` で移動しません。

## 対応するファイル拡張子

現在は次の拡張子を分類対象とします。大文字と小文字は区別しません。

```text
.zip .rar .7z .tar .gz .lzh .epub .mobi .pdf .azw3
```

## 開発時のテスト

全テストは次のコマンドで実行します。

```powershell
uv run python -m unittest discover -s tests -v
```

## 使用ライブラリ

作者名の読みの取得には [SudachiPy](https://github.com/WorksApplications/SudachiPy) と [SudachiDict-full](https://pypi.org/project/SudachiDict-full/) を使用しています。

## ライセンス

ライセンスは [LICENSE](LICENSE) を参照してください。
