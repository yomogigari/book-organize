# Windows Release ZIPの生成

`build-windows-release.ps1` は、v1.0のWindows向けGitHub Release assetを生成します。

このツールはonefile EXEを新しくビルドし、ビルド結果を検証した後、公開に必要な文書とライセンスをまとめます。既存のEXEをそのままZIPへ入れる処理にはしていません。

## 実行方法

リポジトリルートから実行します。

```powershell
.\tools\release\build-windows-release.ps1
```

開発中で未commit変更がある場合だけ、`-AllowDirty` を指定します。

```powershell
.\tools\release\build-windows-release.ps1 -AllowDirty
```

既存の出力を削除して作り直す場合は、`-CleanOutput` を指定します。

```powershell
.\tools\release\build-windows-release.ps1 -CleanOutput
```

既定の出力先は次です。

```text
<repositoryの親>\work\book-organize-v1.0-release-output
```

GitHub Releaseへアップロードするファイルは `artifacts` ディレクトリに生成します。

```text
artifacts\
├─ book-organize-v1.0-windows-x64.zip
└─ SHA256SUMS.txt
```

## Release ZIPの内容

ZIPにはトップディレクトリ `book-organize-v1.0-windows-x64` を作成します。

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

`Apache-2.0.txt` は、Release ZIPへ再配布するSudachiPyとSudachiDict-fullのライセンス本文です。SudachiDict-fullの追加条件は `SudachiDict-full-LEGAL.txt` に保持します。

Nuitkaはビルド時に使用しますが、Release ZIPにはNuitka本体を含めません。

## 自動検証

Release ZIPを生成する前に、プロジェクトの全テストとonefileビルド検証を実行します。

ZIP作成時には、ファイル一覧、空ファイルの有無、内部 `SHA256SUMS.txt`、ZIP展開後に相当する各ファイルのSHA-256を確認します。

`artifacts\SHA256SUMS.txt` はGitHub ReleaseへアップロードするZIP自体のSHA-256です。

すべての検証に成功すると、最後に `RELEASE BUILD RESULT: PASS` と表示します。
