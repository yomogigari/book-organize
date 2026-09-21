# Changelog

## v1.0 — Unreleased

v1.0は、`book-organize` の最初の正式リリースです。

### 追加

- `run`、`list`、`move` を一つのCLIに統合しました。
- 作者名の読みを補正する簡易CSV辞書に対応しました。
- Windows向けのNuitka onefileビルドに対応しました。
- Windowsビルド後にPython版とEXE版の出力を比較する検証を追加しました。

### 変更

- 実行環境をPython 3.12とuvで管理する構成に変更しました。
- 読みの一部に未変換文字が残る場合は、分類コードを `!!` とするようにしました。
- 旧 `make-book-list.py` と `move-book.py` の互換エントリーポイントを削除しました。
- 公開テストデータを架空・試験用の名称へ変更しました。

### 依存関係

- SudachiPy 0.6.11
- SudachiDict-full 20260723

Windows EXEのビルドにはNuitka 4.2.1を使用します。
