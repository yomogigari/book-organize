# book-organize v1.0 Release Notes

v1.0は、`book-organize` の最初の正式リリースです。

`book-organize` は、電子書籍ファイルのファイル名から作者名を抽出し、作者名の読みに基づいて整理用ディレクトリへ分類・移動するCLIツールです。

## Windows版

Windows版は、GitHub Releaseの `book-organize-v1.0-windows-x64.zip` から利用します。ZIPにはonefile形式の `book-organize.exe` と、README、CHANGELOG、ライセンス文書を含めます。

Windows版EXEを使用する場合、Pythonやuvを別にインストールする必要はありません。

EXEは初回実行時に、SudachiDict-fullなどの実行ファイルをユーザーキャッシュへ展開します。展開先は通常、次のディレクトリです。

```text
%LOCALAPPDATA%\book-organize\v1.0
```

v1.0の検証ビルドでは、キャッシュ全体が約377 MBになりました。ビルド内容によって変わる可能性があるため、Windows版を使用する場合は400 MB程度の空き容量を見込んでください。

## Python版

Python版はPython 3.12とuvを使用します。リポジトリを取得した後、依存関係を同期します。

```powershell
uv sync
```

ヘルプは次のコマンドで確認できます。

```powershell
uv run book-organize.py -h
```

## 主な機能

`run` は分類情報を生成した後、同じ結果を使ってファイルを移動します。実際に移動する前に `--dry-run` を指定すると、移動予定だけを確認できます。

`list` はファイルを移動せず、分類情報をCSVまたは標準出力へ出力します。

`move` は既存のCSVに従ってファイルを移動します。

SudachiPyで期待した読みを取得できない作者名は、`--reading-dict` で指定する簡易CSV辞書から補正できます。

## ファイルを移動する前の確認

`run` と `move` は実際のファイルを移動します。最初に `--dry-run` で移動予定を確認してください。

元の配置へ戻す必要がある場合に備え、必要なファイルは実行前にバックアップしてください。

## 読みを取得できない場合

作者名の読みをカタカナとして最後まで取得できない場合、分類コードは `!!` になります。分類コードが `!!` のファイルは `run` と `move` で移動しません。

読みを手動で補正する場合は、`author-readings.csv` などのローカル読み辞書を作成し、`--reading-dict` で指定します。

## ライセンス

`book-organize` 本体のライセンスはRelease ZIPの `LICENSE` を参照してください。

Windows版に含まれる第三者ソフトウェアについては、`THIRD-PARTY-NOTICES.md` と `third-party-licenses` ディレクトリを参照してください。
