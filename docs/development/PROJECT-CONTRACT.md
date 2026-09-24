# Project Contract

この文書は、`book-organize` の実装を変更しても維持する開発上の契約と正本を記録します。

共通の開発標準を自動追従せず、採用した immutable 基準点とこのプロジェクト固有の判断を組み合わせて使用します。

## 0. 開発標準基準点

- Standards source: `development-standards`
- Adopted immutable ref: `5ded388cc78e683689382d7feec420758a1cc382`
- Adopted snapshot / artifact filename: `development-standards-main.zip`
- Adopted snapshot SHA-256: `21ccf70d85c87c14895402fc99384b150b4147998bee2433e87e52df5605e540`
- Adopted on: `2026-09-24`
- Project Contract: `docs/development/PROJECT-CONTRACT.md`
- Update policy: standards の更新は自動追従せず、差分と影響を確認したうえで明示的に採用する。

開発開始時の旧基準点は [../development-baseline.md](../development-baseline.md) に履歴資料として保持します。
この履歴資料は現在の Project Contract を置き換えません。

### 条件付き正本の適用状態

| 領域 | Status | Canonical document | 理由 |
|---|---|---|---|
| Generated artifacts | APPLY | `GENERATED-ARTIFACTS.md` | CSV、Windows EXE、Release ZIP、checksum を生成するため。 |
| ローカル状態 / キャッシュ / output | APPLY | `LOCAL-STATE-CACHE-AND-OUTPUTS.md` | onefile cache、利用者の読み辞書、CSV 出力、build / release output を扱うため。 |
| 設定 / Feature flag の段階展開 | N/A | `CONFIGURATION-AND-FEATURE-ROLLOUT.md` | versioned 設定スキーマや Feature flag を持たないため。 |
| 永続データストア / 復旧 | N/A | `PERSISTENT-DATA-STORES-AND-RECOVERY.md` | database や長期保持する structured store を持たないため。 |
| Background jobs / resumability | N/A | `BACKGROUND-JOBS-AND-RESUMABILITY.md` | background worker、queue、resume 機構を持たないため。 |
| Network API / secrets | N/A | `NETWORK-API-AND-SECRETS.md` | 製品 runtime は外部 API や認証情報を使用しないため。 |
| プラグイン / 拡張機能 | N/A | `PLUGIN-AND-EXTENSION-ARCHITECTURE.md` | plugin discovery や extension API を持たないため。 |
| ソフトウェア更新 / ロールバック | N/A | `SOFTWARE-UPDATE-AND-ROLLBACK.md` | self-update や update feed を持たないため。 |
| CI/CD / automation | N/A | `CI-CD-AND-AUTOMATION.md` | 現在の Release はローカル build と手動公開で行うため。 |

上記の条件が変わる変更では、この表を同じ変更単位で再評価します。

## 1. 正式名称と識別子

- 製品名: `book-organize`
- リポジトリ名: `book-organize`
- CLI entry point: `book-organize.py`
- Windows executable: `book-organize.exe`
- Primary package: `book_organize`
- Release tag: `vX.Y`
- Windows Release asset: `book-organize-vX.Y-windows-x64.zip`

旧 `make-book-list.py` と `move-book.py` は v1.0 で削除済みです。
互換 entry point として提供しません。

## 2. 目的

`book-organize` は、電子書籍ファイルのファイル名から作者名を抽出し、読みを分類コードへ変換して整理用ディレクトリへ移動する CLI ツールです。

分類だけを確認する用途、既存 CSV に従って移動する用途、作者名の読みを利用者が補正する用途も同じ CLI で提供します。

## 3. 非目的

電子書籍の内容解析、書誌情報のオンライン取得、閲覧機能、ライブラリ database の管理は対象にしません。

ファイル名から抽出した作者名や SudachiPy の読みが常に正しいことは保証しません。
必要な補正は簡易読み辞書で明示的に与えます。

## 4. 安全境界

### 読み取り

`list` と `run` は、対象ディレクトリのファイル名と必要なローカル入力を読み取ります。

`move` は、利用者が指定した CSV と対象ディレクトリを読み取ります。

### 書き込み

`list --out` と `run --out` は、利用者が指定した CSV を出力します。

`run` と `move` は、整理用ディレクトリを作成し、対象ファイルを移動します。

### 実行前確認

ファイル移動を行う `run` と `move` では `--dry-run` を標準の事前確認手段とします。

必要なファイルのバックアップは利用者が実行前に用意します。

## 5. 正本

| 対象 | 正本 | 補足 |
|---|---|---|
| Source | `src/book_organize/` | 主要ロジックの正本。 |
| CLI entry point | `book-organize.py` | 利用者が実行する root entry point。 |
| Dependency versions | `pyproject.toml`, `uv.lock` | Python と依存関係の再現に使用する。 |
| User reading override | 利用者が指定する簡易 CSV | `author-readings.csv` は既定名であり、Git 管理しない。 |
| Generated classification CSV | 実行時生成物 | Source の正本へ逆流させない。 |
| Windows build output | `tools/windows-build` による生成物 | Source の正本へ逆流させない。 |
| Windows Release ZIP | `tools/release` による凍結候補 | 公開後の asset と checksum を照合する。 |

## 6. リポジトリと Git

- Visibility: Public
- Primary repository: `https://github.com/yomogigari/book-organize`
- Primary remote: `origin`
- Primary branch: `main`
- Release tag: annotated tag を使用する。

Git の変更確認、tracked rename / move、push 後確認などの共通手順は、採用した `development-standards` を正本とします。
この Project Contract では project 固有値と例外だけを定義します。

## 7. 外部アクセス

### 製品 runtime

現在の CLI は、分類・移動処理のために外部 API や認証情報を必要としません。

将来 runtime のネットワークアクセスを追加する場合は、接続先、timeout、retry、response 検証、秘密情報の境界を Project Contract に追加します。

### 開発・ビルド

`uv sync`、依存関係解決、Nuitka や build tool の取得では、package index へのネットワークアクセスが発生する場合があります。

再現性は `pyproject.toml`、`uv.lock`、固定した Python / Nuitka / Sudachi の version と build report で確認します。

## 8. Version と開発 revision

- 公開 version: `vX.Y`
- 開発 revision: `vX.Y-rNN`
- 公開後の最初の実変更: 原則 `vX.Y-r01`
- 同一公開 version 内: `r02`、`r03` のように単調増加する。
- 次の公開 version へ更新した後: 新しい公開 version の `r01` へリセットする。
- revision の消費条件: 実変更を開始した時点で使用し、単なるコピーでは消費しない。

`-rNN` の一般規則は `development-standards` の `VERSIONING-AND-TAGS.md` を正本とします。

### v1.0 系列の移行例外

v1.0 公開前に `v1.0-r01` から `v1.0-r13` を使用し、今回の standards 採用前に v1.0 公開後の作業を `v1.0-r14` として開始済みです。

今回の未 commit 論理変更は、利用者判断により `v1.0-r14` のまま継続します。
v1.0 系列で後続 revision が必要な場合は、この既存系列を単調増加させます。

次の公開 version へ更新した後は、この移行例外を持ち越さず、新しい公開 version の `r01` から開始します。

## 9. 固定インターフェース

正式に提供する CLI entry point は `book-organize.py` です。

| Interface | 実行方法 | 受入確認 |
|---|---|---|
| Root help | `uv run book-organize.py -h` | root help に全サブコマンドの案内がある。 |
| `run` | `uv run book-organize.py run ...` | dry-run と実移動を確認する。 |
| `list` | `uv run book-organize.py list ...` | CSV / stdout の分類結果を確認する。 |
| `move` | `uv run book-organize.py move ...` | CSV に従う dry-run と実移動を確認する。 |
| Windows EXE | `book-organize.exe ...` | Python 版との semantic / byte equality を確認する。 |

v1.0 の CSV 列構成と簡易読み辞書形式は README に記載します。
公開済み契約を変更する場合は、CHANGELOG と Release Notes で互換性影響を明示します。

## 10. テストと受入基準

全自動テストの標準 command は次です。

```powershell
uv run python -m unittest discover -s tests -v
```

Release build では、Python 版と Windows EXE 版の `list` CSV を byte-for-byte で比較します。

Release build では、Python 版と Windows EXE 版の `run --dry-run` 標準出力も byte-for-byte で比較します。

onefile では初回展開、キャッシュ内 `system.dic`、2 回目実行を Windows 実機で確認します。

README、CLI help、固定 asset 名、ライセンス文書などの利用者向け契約は regression test で確認します。

## 11. 文書と言語

日本語文書を正本とします。

現在、別の英語版文書は提供しません。

README は利用者向けの入口とし、ビルド・Release の詳細は `tools/` 配下の README へ分離します。

過去の Release Notes、確定済み build 記録、開発開始時 baseline は、文章規則だけを理由に遡って書き換えません。

## 12. ローカル状態、キャッシュ、生成出力

| 種類 | 既定パス / 導出規則 | 正本性 | 削除可能性 | 外部共有 |
|---|---|---|---|---|
| 読み辞書 | 利用者指定。既定名 `author-readings.csv` | User-owned override | 利用者判断 | 内容確認が必要 |
| onefile cache | `%LOCALAPPDATA%\book-organize\v1.0` | Cache | 再展開可能 | 原則不要 |
| 分類 CSV | `--out` で利用者指定 | Generated output | 利用者判断 | 内容確認が必要 |
| Build output | repository の親の `work` 配下 | Generated output | 再生成可能 | 公開対象ではない |
| Release candidate | `book-organize-v1.0-release-output` | Frozen candidate | 公開確認後に整理可能 | asset だけを公開 |

onefile cache は source や user data の正本として扱いません。

Release candidate は、内容を変更した場合に同じ candidate とみなさず、再生成と checksum 再確認を行います。

## 13. Platform、改行コード、timezone

Windows x64 を Windows EXE の配布対象とします。

Python 版は Python 3.12 と uv を基準環境とします。
Windows EXE 以外の配布形態は、個別に検証した範囲を超えて対応済みと表現しません。

`.gitattributes` では、Markdown、Python、TOML、lock、JSON、CSV 等を LF、PowerShell / BAT / CMD を CRLF とします。

日本語を含む通常テキストは UTF-8 を使用します。
形式上 BOM が必要なファイルだけ例外とします。

Release ZIP の member timestamp は JST の wall-clock time を使用します。
Release tool では IANA tzdata に依存せず UTC+09:00 の固定 offset を使用します。

## 14. Public / Private データ境界

Public repository には source、公開文書、架空の test data、build / release tool を置きます。

利用者の実ファイル名、実作者名を含む読み辞書、ローカル path、認証情報、内部専用 data は公開物へ持ち込みません。

Public 向け test / example data は、実在人物を想起しにくい架空・試験用名称を使用します。

Release 前は current tree、必要な Git history、Release asset を別々に確認します。

## 15. 長期使用

CLI subcommand、主要 option、CSV format、読み辞書 format、Release asset 名は、公開後の利用者向け契約として扱います。

互換性を破る変更では、version と Release Notes で影響を明示します。

Python、SudachiPy、SudachiDict-full、Nuitka の更新は lock / pin の変更として明示的に検証します。

v1.0 の onefile cache path と release tool には version 固有値があります。
次の公開 version では、cache path、asset 名、Release Notes、release tool の version 値を同じ変更単位で確認します。

## 16. 共通標準からの例外

v1.0 系列の開発 revision だけ、standards 採用時の移行例外があります。
今回の未 commit 論理変更は `v1.0-r14` のまま継続し、次の公開 version へ更新した後から標準の `r01` リセットを適用します。

それ以外に、採用した開発標準の必須規則に対する project 固有の例外はありません。
