# Windows Release ZIP の生成

このディレクトリは、Windows 向け GitHub Release asset を生成し、公開前の配布物を検証するツールを管理します。

`build-windows-release.ps1` は既存 EXE を再利用しません。
onefile EXE を新しくビルドし、ビルド結果を検証した後、公開に必要な文書とライセンスをまとめます。

## 実行条件

Release candidate は clean worktree と確定した Git HEAD から生成します。

リポジトリルートから次のコマンドを実行します。

```powershell
.\tools\release\build-windows-release.ps1
```

既存の出力を削除して作り直す場合は `-CleanOutput` を指定します。

```powershell
.\tools\release\build-windows-release.ps1 -CleanOutput
```

`-AllowDirty` は未 commit 変更を含む開発中の検証だけに使用します。
正式な Release candidate では使用しません。

```powershell
.\tools\release\build-windows-release.ps1 -AllowDirty
```

## 出力先

v1.0 の既定出力先は次です。

```text
<repositoryの親>\work\book-organize-v1.0-release-output
```

GitHub Release へアップロードするファイルは `artifacts` ディレクトリに生成します。

```text
artifacts\
├─ book-organize-v1.0-windows-x64.zip
└─ SHA256SUMS.txt
```

`artifacts\SHA256SUMS.txt` は、GitHub Release へアップロードする ZIP 自体の SHA-256 を記録します。

## Release ZIP の内容

ZIP にはトップディレクトリ `book-organize-v1.0-windows-x64` を作成します。

```text
book-organize-v1.0-windows-x64\
├─ book-organize.exe
├─ README.md
├─ CHANGELOG.md
├─ LICENSE
├─ THIRD-PARTY-NOTICES.md
├─ SHA256SUMS.txt
└─ third-party-licenses\
   ├─ Python-3.12-LICENSE.txt
   ├─ Apache-2.0.txt
   └─ SudachiDict-full-LEGAL.txt
```

`Apache-2.0.txt` は、Release ZIP へ再配布する SudachiPy と SudachiDict-full のライセンス本文です。
SudachiDict-full の追加条件は `SudachiDict-full-LEGAL.txt` に保持します。

Nuitka はビルド時に使用しますが、Release ZIP には Nuitka 本体を含めません。

## 自動検証

Release ZIP を生成する前に、プロジェクトの全テストと onefile ビルド検証を実行します。

生成後は次を確認します。

- 期待するファイル集合
- 空ファイルの不在
- ZIP 内部の `SHA256SUMS.txt`
- ZIP 内の各ファイルの SHA-256
- `book-organize.exe -h`
- ZIP 内のファイル一覧
- 公開 ZIP 自体の SHA-256

すべての検証に成功すると、最後に `RELEASE BUILD RESULT: PASS` と表示します。

## Release candidate の扱い

`release-summary.txt` には、生成元の repository HEAD、asset の SHA-256、EXE の SHA-256、検証結果を記録します。

公開候補を確定した後は ZIP を変更しません。
内容を変更した場合は再生成し、SHA-256 と検証結果を更新します。

GitHub Release へ公開した後は、公開 asset の digest を凍結済み candidate と照合します。

## Version 固有値

現在の release tool は v1.0 の asset 名と出力先をコード上で固定しています。
次の公開 version では、Release candidate を生成する前に version 固有値、cache path、asset 名、Release Notes の整合を確認してください。
