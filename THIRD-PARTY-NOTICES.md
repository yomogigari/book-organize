# Third-Party Notices

`book-organize` は、作者名の読みの取得とWindows EXEの実行に第三者ソフトウェアを使用します。

この文書は、v1.0で直接使用する主要な第三者コンポーネントとライセンスを示します。Windows向けRelease ZIPには、再配布するコンポーネントのライセンス本文も同梱します。

## CPython

Windows EXEはCPython 3.12系のランタイムを含みます。

- Project: Python
- License: Python Software Foundation License Version 2
- Website: https://www.python.org/
- License information: https://docs.python.org/3.12/license.html

## SudachiPy

作者名の形態素解析と読みの取得にはSudachiPy 0.6.11を使用します。

- Project: SudachiPy
- Version: 0.6.11
- License: Apache License 2.0
- Website: https://pypi.org/project/SudachiPy/

## SudachiDict-full

SudachiPyのシステム辞書にはSudachiDict-full 20260723を使用します。

- Project: SudachiDict-full
- Version: 20260723
- License: Apache License 2.0
- Website: https://pypi.org/project/SudachiDict-full/

SudachiDictにはUniDicとNEologdの一部が含まれます。辞書データに関する詳細な条件は、SudachiDict-fullに付属する `LEGAL` と `LICENSE-2.0.txt` を参照してください。Windows向けRelease ZIPでは、これらのファイルを第三者ライセンスとして同梱します。

## Nuitka

Windows EXEのビルドにはNuitka 4.2.1を使用します。Nuitkaは通常の実行時依存関係には含めません。

- Project: Nuitka
- Version: 4.2.1
- License: Apache License 2.0
- Website: https://nuitka.net/

Nuitkaで生成したWindows EXEには、`book-organize` が実行時に必要とするPythonランタイムと依存パッケージを含めます。

## Windows Release ZIPに同梱するライセンス本文

Windows向けRelease ZIPでは、再配布する実行時コンポーネントのライセンス本文を `third-party-licenses` ディレクトリへ同梱します。

- `Python-3.12-LICENSE.txt`: Windows EXEに含まれるCPython 3.12系ランタイム
- `Apache-2.0.txt`: SudachiPy 0.6.11とSudachiDict-full 20260723
- `SudachiDict-full-LEGAL.txt`: SudachiDict-fullに含まれるUniDicとNEologd由来データの条件

Nuitka 4.2.1はビルド時に使用しますが、Release ZIPにはNuitka本体を含めません。
