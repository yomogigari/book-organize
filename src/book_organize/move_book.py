# !/usr/bin/env python
# coding: utf-8
"""
make-book-list.py が生成したCSVファイルの情報に基づいてファイルを移動するツール

usage:
  python move-book.py --csv CSV --dir DIR [--dry-run] [--first-dir]

オプション:
  --csv       入力CSVファイル（必須）
  --dir       処理を行うベースディレクトリ（必須）
  --dry-run   実際の処理を行わず、実行予定の処理を表示
  --first-dir 最初の階層ディレクトリのみを使用してファイルを移動する
"""
import os
import sys
import argparse
import csv
import re
from pathlib import Path

# Windows環境でUTF-8出力を設定
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def is_valid_directory_code(code):
    """カタカナ2文字であるかチェック"""
    return bool(re.match(r'^[ァ-ヶー]{2}$', code))


def get_directory_path(base_dir, dir_code, first_dir=False):
    """
    ディレクトリパスを生成
    first_dir=True のときは一階層目 (例: 「ア行」) のみ
    """
    first_char = dir_code[0]
    if first_dir:
        return Path(base_dir) / f"{first_char}行"
    else:
        return Path(base_dir) / f"{first_char}行" / dir_code


def process_file(row, base_dir, dry_run=False, first_dir=False):
    """ファイルの処理を実行"""
    dir_code = row[0]
    filename = row[-1]  # 最後のカラムがファイル名

    if not is_valid_directory_code(dir_code):
        print(f"警告: 無効なディレクトリコード '{dir_code}' - スキップします。", file=sys.stderr)
        return

    # 移動元のファイルパス
    source_file = Path(base_dir) / filename

    # 移動先のディレクトリパス
    target_dir = get_directory_path(base_dir, dir_code, first_dir=first_dir)
    target_file = target_dir / filename

    if dry_run:
        print(f"mkdir -p {target_dir}")
        print(f"mv {source_file} {target_file}")
    else:
        try:
            # ディレクトリ作成
            target_dir.mkdir(parents=True, exist_ok=True)

            # ファイルが存在する場合のみ移動
            if source_file.exists():
                source_file.rename(target_file)
                print(f"移動完了: {filename} -> {target_dir}")
            else:
                print(f"警告: ファイルが見つかりません: {filename}", file=sys.stderr)
        except Exception as e:
            print(f"エラー: {filename} の処理中に問題が発生しました: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='make-book-list.py が生成したCSVファイルの情報に基づいてファイルを移動するツール',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--csv', type=str, required=True, help='入力CSVファイル（必須）')
    parser.add_argument('--dir', type=str, required=True, help='処理を行うベースディレクトリ（必須）')
    parser.add_argument('--dry-run', action='store_true', help='実際の処理を行わず、実行予定の処理を表示')
    parser.add_argument('--first-dir', action='store_true',
                        help='最初の階層ディレクトリのみを使用してファイルを移動する')

    args = parser.parse_args()

    # ベースディレクトリの存在確認
    if not os.path.isdir(args.dir):
        print(f"エラー: 指定されたディレクトリが存在しません: {args.dir}", file=sys.stderr)
        sys.exit(1)

    try:
        # CSVファイルの読み込み
        if args.csv:
            with open(args.csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    process_file(row, args.dir, dry_run=args.dry_run, first_dir=args.first_dir)
        else:
            reader = csv.reader(sys.stdin)
            for row in reader:
                process_file(row, args.dir, dry_run=args.dry_run, first_dir=args.first_dir)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
