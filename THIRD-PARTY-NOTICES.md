# Third-Party Notices

`book-organize` は、作者名の読みの取得と Windows EXE の実行に第三者ソフトウェアを使用します。

この文書は、v1.0 で直接使用する主要な第三者コンポーネントとライセンスを示します。
Windows 向け Release ZIP には、再配布するコンポーネントのライセンス本文も同梱します。

## CPython

Windows EXE は CPython 3.12 系のランタイムを含みます。

- Project: Python
- License: Python Software Foundation License Version 2
- Website: https://www.python.org/
- License information: https://docs.python.org/3.12/license.html

## SudachiPy

作者名の形態素解析と読みの取得には SudachiPy 0.6.11 を使用します。

- Project: SudachiPy
- Version: 0.6.11
- License: Apache License 2.0
- Website: https://pypi.org/project/SudachiPy/

## SudachiDict-full

SudachiPy のシステム辞書には SudachiDict-full 20260723 を使用します。

- Project: SudachiDict-full
- Version: 20260723
- License: Apache License 2.0
- Website: https://pypi.org/project/SudachiDict-full/

SudachiDict-full には UniDic と NEologd の一部が含まれます。
辞書データに関する条件は、SudachiDict-full に付属する `LEGAL` と `LICENSE-2.0.txt` を参照してください。

## Nuitka

Windows EXE のビルドには Nuitka 4.2.1 を使用します。
Nuitka はビルド時だけ使用し、通常の実行時依存関係には含めません。

- Project: Nuitka
- Version: 4.2.1
- License: Apache License 2.0
- Website: https://nuitka.net/

Nuitka で生成した Windows EXE には、`book-organize` が実行時に必要とする Python ランタイムと依存パッケージを含めます。

## Windows Release ZIP に同梱するライセンス本文

Windows 向け Release ZIP では、再配布する実行時コンポーネントのライセンス本文を `third-party-licenses` ディレクトリへ同梱します。

- `Python-3.12-LICENSE.txt`: Windows EXE に含まれる CPython 3.12 系ランタイム
- `Apache-2.0.txt`: SudachiPy 0.6.11 と SudachiDict-full 20260723
- `SudachiDict-full-LEGAL.txt`: SudachiDict-full に含まれる UniDic と NEologd 由来データの条件

Nuitka 4.2.1 はビルド時に使用しますが、Release ZIP には Nuitka 本体を含めません。
