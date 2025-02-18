# make-book-list.py, move-book.py

電子書籍ファイルを自動分類するためのCSVデータの生成ツール(make-book-list.py)と、生成データを用いたファイルの移動ツール(move-book.py)。

著者名をカタカナに変換後に先頭2文字を50音表の行ごとに分類し、移動先のディレクトリ名とします。

Python はあまりわかっていないので習作です。整理してライブラリ化したいですが、どうなることやら…

## 導入

著者名からカタカナへの変換は日本語形態素解析器の Sudachi の Python 版である SudachiPy と Sudachi 辞書(full)を使用するため導入をおこなってください。

```bash
pip install sudachipy
pip install sudachidict_full
```

## 使用例

make-book-list.py で分類用のCSVデータを作成し、そのCSVデータを用いて move-book.py でファイル移動をおこないます。

### CSVデータ作成

make-book-list.py を起動すると指定ディレクトリ内のファイル名一覧を読み込み、 SudachiPy で著者名のカタカナ変換をおこないます。変換結果のCSVは1列目が移動先のディレクトリ名作成用情報、変換経緯の情報が続き最終列がファイル名です。

カタカナ変換ができなかった場合、1列目は'!!'となりますので必要に応じて Sudachi のユーザー辞書登録、手動でのカナ記入などをおこなってください。


```bash
$ python make-book-list.py -h
usage: make-book-list.py [-h] [--dir DIR] [--short] [--out OUT]

SudachiPy を用いてファイル名から抽出した文字列のカタカナ表記および変換情報を出力します。カタカナ表記に変更できない場合は!!を出力します。

options:
  -h, --help  show this help message and exit
  --dir DIR   対象ディレクトリ。指定がなければ起動ディレクトリを使用
  --short     短縮形式で出力
  --out OUT   出力先ファイル名。指定がなければ標準出力に出力

$ ls -l /E-book
合計 119M
-rw-r--r-- 1 m-kim m-kim  29M  8月 18  2022 (一般コミック) [A-01] ももたろう .zip
-rw-r--r-- 1 m-kim m-kim  67M  2月 18 11:54 (一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip
-rw-r--r-- 1 m-kim m-kim  24M  3月 13  2017 [香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいられません～.mobi
-rw-r--r-- 1 m-kim m-kim 177K  2月 18 09:49 [明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub

$ python make-book-list.py --dir /E-book --out book.csv

$ cat type book.csv
!!,a-,a-レイイチ,a-レイイチ,A-01,(一般コミック) [A-01] ももたろう .zip
アカ,アカ,アカシロクロウ,アカシロクロウ,明石六郎,[明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub
カタ,カツ,カツキキコウミヤ,カツキキゴウミヤ,香月 美夜,[香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいら れません～.mobi
ヤマ,ヨモ,ヨモキカリ,ヨモギガリ,蓬がり,(一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip
```

### ファイル移動


make-book-list.py で作成したCSVファイルと処理ディレクトリを指定するとCSVファイルの内容に従いディレクトリの作成とファイル移動をおこないます。
CSVの1列目が'!!'のレコードはファイル移動はおこなわないません。

 --dry-run では実際のディスク操作はおこなわずに処理内容を出力します。

```bash
$ python move-book.py -h
usage: move-book.py [-h] [--csv CSV] --dir DIR [--dry-run]

make-book-list.py が生成したCSVファイルの情報に基づいてファイルを移動するツール

options:
  -h, --help  show this help message and exit
  --csv CSV   入力CSVファイルのパス。指定がなければ標準入力から読み込み
  --dir DIR   処理を行うベースディレクトリ（必須）
  --dry-run   実際の処理を行わず、実行予定の処理を表示

$ python move-book.py --dir /E-book --csv book.csv --dry-run
警告: 無効なディレクトリコード '!!' - スキップします。
mkdir -p /E-book/ア行/アカ
mv /E-book/[明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub /E-book/ア行/アカ/[明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub
mkdir -p /E-book/カ行/カタ
mv /E-book/[香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいられません～.mobi /E-book/カ行/カタ/[香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいられません～.mobi
mkdir -p /E-book/ヤ行/ヤマ
mv /E-book/(一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip /E-book/ヤ行/ヤマ/(一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip

$ python move-book.py --dir /E-book --csv book.csv
警告: 無効なディレクトリコード '!!' - スキップします。
移動完了: [明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub -> /E-book/ア行/アカ
移動完了: [香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいられません～.mobi -> /E-book/カ行/カタ
移動完了: (一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip -> /E-book/ヤ行/ヤマ

$ cd /E-book; ls -R /E-book
.:
(一般コミック) [A-01] ももたろう .zip   ア行/   カ行/   ヤ行/

./ア行:
アカ/

./ア行/アカ:
[明石六郎] ヒールが使えないソロヒーラー、女尊男卑世界へ帰還す.epub

./カ行:
カタ/

./カ行/カタ:
[香月　美夜] 本好きの下剋上　～司書になるためには手段を選んでいられません～.mobi

./ヤ行:
ヤマ/

./ヤ行/ヤマ:
(一般コミック) [蓬がり×よもーぎ] サンプル 第01巻.zip
```