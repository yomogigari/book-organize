# !/usr/bin/env python
# coding: utf-8
"""分類情報に基づいて電子書籍ファイルを整理用ディレクトリへ移動する。"""
import sys
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


def process_rows(rows, base_dir, dry_run=False, first_dir=False):
    """分類行を順番に処理する。"""
    for row in rows:
        if row:
            process_file(row, base_dir, dry_run=dry_run, first_dir=first_dir)


def read_csv_rows(csv_path):
    """UTF-8の分類用CSVを読み込む。"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        return list(csv.reader(f))
