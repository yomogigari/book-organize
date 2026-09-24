# Changelog

## Unreleased

### 変更

- `development-standards-main.zip` の固定 snapshot を開発標準として採用し、`docs/development/PROJECT-CONTRACT.md` を Project Contract として追加して、基準点と project 固有契約を記録した。
- Project Contract の v1.0-r14 移行例外を commit 済み状態へ更新し、次の公開 version への revision リセット時点を `development-standards` と一致させた。
- README、第三者ライセンス案内、Windows build / Release tool の現行文書を開発標準の文章規則と責任分界に沿って再構成した。
- v1.0 Release Notes と開発開始時 baseline は、確定済み履歴資料として変更対象から除外した。

### 互換性

- CLI の挙動、CSV format、簡易読み辞書 format、v1.0 Release asset の仕様は変更していない。

## v1.0 — 2026-09-22

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
