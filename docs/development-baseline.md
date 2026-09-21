# 開発基準 — 2026-09-21

## 対象

この文書は、2026年9月21日に開発へ使用した `book-organize-main.zip` の内容を基準として記録する。

添付ZIPにはGit管理情報が含まれていないため、Gitのcommit IDはこの環境では確認できない。基準の同一性は、元ZIPと主要ファイルのSHA-256で確認する。

## 元ZIP

`book-organize-main.zip`

SHA-256は成果物作成時に確認する。

## 既存ファイルのSHA-256

```text
b471380cdaf0401cba49e90e2e22a8c171170001a8aab529a83af250af9de91e  .gitignore
3f36f34a79efb340af843deb2db096ac056a388438ea4a93fd1d35afc7e4a4f6  LICENSE
76cd888d4552af32d90028737f52e41812f88d1938a7a8d6dd54ca43c771acdb  README.md
8357f23b46b4cd296b30651ef57058da9926589685dc64647316dddf22b300a8  make-book-list.py
c2337ec41e55ccb67e11be2b0599358c0a647d924433e8ba294da481fed435c4  move-book.py
```

## 依存関係の更新基準

今回の開発では、次のバージョンを更新先とする。

- SudachiPy 0.6.11
- SudachiDict-full 20260723
- Python 3.12

`pyproject.toml` で依存バージョンを指定する。`uv.lock` は依存パッケージを取得できる環境で生成し、生成後にリポジトリへ追加する。

SudachiDict-full 20260723.1 は SudachiPy 0.7.0 以上を要求するが、2026年9月21日時点でPyPIから利用できるSudachiPyの最新リリースは0.6.11である。このため、SudachiPy 0.6.11と互換性のあるSudachiDict-full 20260723を採用する。

## baselineテストの範囲

最初のテストでは、外部辞書の内容に依存しない既存規則を固定する。

- ファイル名から作者名を抽出する規則
- `×` より後ろを作者名から除外する規則
- NFKCによる英数字の正規化
- カタカナの正規化
- 分類用2文字コードの生成
- CSVフィールドの既存エスケープ規則
- 移動先ディレクトリの生成
- 無効な分類コードを移動対象から除外する規則
- ファイル移動処理

SudachiPyとSudachiDict-fullの実データを使う変換結果は、依存関係を導入できる環境で別途確認する。
