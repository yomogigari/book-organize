#!/usr/bin/env python
# coding: utf-8
"""
SudachiPyを用いたファイル名処理スクリプト

usage:
  python make-book-list.py [--dir DIRECTORY] [--out OUTPUTFILE]

オプション:
  --dir    対象ディレクトリ。指定がなければ起動ディレクトリを利用
  --short  短縮形式で出力
  --out    出力先ファイル名。指定がなければ標準出力へ出力
"""
import os
import sys
import argparse
import re
import unicodedata
from sudachipy import dictionary, tokenizer

# 対象ファイルの拡張子リスト（小文字で比較）
TARGET_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.lzh',
                     '.epub', '.mobi', '.pdf', '.azw3'}

# 濁音・半濁音・拗音・促音の正規化マッピング
NORMALIZATION_MAP = {
    # 拗音・小文字 → 基本形
    'ァ': 'ア', 'ィ': 'イ', 'ゥ': 'ウ', 'ェ': 'エ', 'ォ': 'オ',
    'ャ': 'ヤ', 'ュ': 'ユ', 'ョ': 'ヨ',
    'ッ': 'ツ',
    # 濁音・半濁音 → 基底文字
    'ガ': 'カ', 'ギ': 'キ', 'グ': 'ク', 'ゲ': 'ケ', 'ゴ': 'コ',
    'ザ': 'サ', 'ジ': 'シ', 'ズ': 'ス', 'ゼ': 'セ', 'ゾ': 'ソ',
    'ダ': 'タ', 'ヂ': 'チ', 'ヅ': 'ツ', 'デ': 'テ', 'ド': 'ト',
    'バ': 'ハ', 'ビ': 'ヒ', 'ブ': 'フ', 'ベ': 'ヘ', 'ボ': 'ホ',
    'パ': 'ハ', 'ピ': 'ヒ', 'プ': 'フ', 'ペ': 'ヘ', 'ポ': 'ホ',
    'ヴ': 'ウ',
}

# カタカナの各行の代表値マッピング
KANA_GROUPS = {
    'ア': set(['ア', 'イ', 'ウ', 'エ', 'オ']),
    'カ': set(['カ', 'キ', 'ク', 'ケ', 'コ']),
    'サ': set(['サ', 'シ', 'ス', 'セ', 'ソ']),
    'タ': set(['タ', 'チ', 'ツ', 'テ', 'ト']),
    'ナ': set(['ナ', 'ニ', 'ヌ', 'ネ', 'ノ']),
    'ハ': set(['ハ', 'ヒ', 'フ', 'ヘ', 'ホ']),
    'マ': set(['マ', 'ミ', 'ム', 'メ', 'モ']),
    'ヤ': set(['ヤ', 'ユ', 'ヨ']),
    'ラ': set(['ラ', 'リ', 'ル', 'レ', 'ロ']),
    'ワ': set(['ワ', 'ヲ', 'ン']),
}

def escape_csv_field(field: str) -> str:
    """
    CSV フィールドのエスケープ処理を行う
    - カンマ、引用符（',"）を含む場合はダブルクォートで囲む
    - フィールド内のダブルクォートは二重にする
    """
    if not isinstance(field, str):
        field = str(field)
    
    needs_quotes = (',' in field or '"' in field or "'" in field)
    if needs_quotes:
        # ダブルクォートを二重にエスケープ
        field = field.replace('"', '""')
        # フィールド全体をダブルクォートで囲む
        field = f'"{field}"'
    return field

def normalize_katakana(text: str) -> str:
    """
    濁音・半濁音・拗音・促音をマッピングにより正規化する
    """
    return "".join(NORMALIZATION_MAP.get(ch, ch) for ch in text)

def get_kana_group(ch: str) -> str:
    """
    カタカナ1文字からグループ代表（例：カ行なら「カ」）を返す。
    グループに属さなければそのまま返す
    """
    for key, group in KANA_GROUPS.items():
        if ch in group:
            return key
    return ch

def is_katakana(text: str) -> bool:
    """
    文字列がすべてカタカナであるかチェックする
    """
    return all(unicodedata.name(ch).startswith('KATAKANA') for ch in text)

def build_group_string(kana_text: str, raw_kana: str) -> str:
    """
    カタカナ表記の先頭2文字それぞれをグループ代表に置き換え、連結する。
    raw_kanaにカタカナ以外の文字が含まれている場合は "!!" を返す。
    例：'キヨ' → 'カ' + 'ヤ' = 'カヤ'
    """
    if not kana_text:
        return ""
    
    result = []
    for ch in kana_text[:2]:
        result.append(get_kana_group(ch))
    return "".join(result)

def extract_name(filename: str) -> str:
    """
    ファイル名から半角の [と] に囲まれた文字列を抽出し、
    '×'が含まれる場合はその前まで抽出、アルファベットを半角化する。
    該当文字列がない場合は "!!" を返す。
    """
    # 半角角括弧で囲まれた文字列を抽出
    m = re.search(r'\[([^\]]+)\]', filename)
    if m:
        name = m.group(1)
        # '×'が含まれる場合、その直前まで切り出す
        if '×' in name:
            name = name.split('×')[0]
        # アルファベットが含まれる場合に半角変換（NFKC正規化で全角→半角が可能）
        name = unicodedata.normalize('NFKC', name)
        return name
    else:
        return "!!"

def main():
    try:
        parser = argparse.ArgumentParser(
            description="SudachiPy を用いてファイル名から抽出した文字列のカタカナ表記および変換情報を出力します。カタカナ表記に変更できない場合は!!を出力します。"
        )
        parser.add_argument('--dir', type=str, default=os.getcwd(), help='対象ディレクトリ。指定がなければ起動ディレクトリを使用')
        parser.add_argument("--short", action="store_true", help="短縮形式で出力")
        parser.add_argument('--out', type=str, help='出力先ファイル名。指定がなければ標準出力に出力')
        args = parser.parse_args()

        # Windows環境でUTF-8出力を行うための設定
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='utf-8')

        target_dir = args.dir
        if not os.path.isdir(target_dir):
            print(f"エラー: 指定されたディレクトリ '{target_dir}' は存在しません。", file=sys.stderr)
            sys.exit(1)

        # 対象ディレクトリ内のファイル一覧取得（ファイル名のみ）
        try:
            files = os.listdir(target_dir)
        except Exception as e:
            print(f"ディレクトリ読み込みエラー: {str(e)}", file=sys.stderr)
            sys.exit(1)

        # 対象ファイルのみピックアップ（拡張子による判定、大小文字区別しない）
        target_files = []
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in TARGET_EXTENSIONS:
                target_files.append(f)

        # キャッシュ：抽出名 → (生Sudachi出力, 正規化後カタカナ)
        sudachi_cache = {}

        # 事前に抽出する名前の集合を構築（"!!"は対象外）
        names_to_process = set()
        file_info_list = []  # 各要素： (extracted_name, filename)
        for f in target_files:
            extracted = extract_name(f)
            file_info_list.append((extracted, f))
            if extracted != "!!":
                names_to_process.add(extracted)

        # Sudachi の初期化 (dict="full" で初期化、分割モードは C)
        sudachi_tokenizer = dictionary.Dictionary(dict="full").create()
        mode = tokenizer.Tokenizer.SplitMode.C

        # 一括処理に近い形でキャッシュ作成
        for name in names_to_process:
            try:
                tokens = sudachi_tokenizer.tokenize(name, mode)
                raw_kana = "".join(token.reading_form() for token in tokens)
            except Exception as e:
                print(f"Sudachi解析エラー '{name}': {str(e)}", file=sys.stderr)
                raw_kana = ""
            normalized_kana = normalize_katakana(raw_kana)
            sudachi_cache[name] = (raw_kana, normalized_kana)

        # CSV行を構築
        output_rows = []
        for extracted, fname in file_info_list:
            if extracted != "!!":
                raw_kana, normalized_kana = sudachi_cache.get(extracted, ("", ""))
            else:
                raw_kana, normalized_kana = ("!!", "!!")
            # カタカナ表記の先頭2文字
            head2 = normalized_kana[:2]
            # グループ代表文字列を作成
            group_str = build_group_string(normalized_kana, raw_kana)
            
            if group_str and not is_katakana(group_str):
                group_str = "!!"

            # 各項目： group_str, head2, normalized_kana, raw_kana, extracted, ファイル名
            if args.short:
                row = [group_str, fname]
            else:
                row = [group_str, head2, normalized_kana, raw_kana, extracted, fname]
            output_rows.append(row)

        # ソート：カタカナ表記の先頭2文字およびファイル名で昇順ソート
        if args.short:
            output_rows.sort(key=lambda x: (x[0], x[1]))
        else:
            output_rows.sort(key=lambda x: (x[0], x[5]))

        # 結果の出力（UTF-8）
        output_lines = []
        for row in output_rows:
            # 各フィールドをエスケープしてからカンマで結合
            escaped_row = [escape_csv_field(field) for field in row]
            output_lines.append(",".join(escaped_row))

        output_text = "\n".join(output_lines)

        if args.out:
            try:
                with open(args.out, "w", encoding="utf-8") as f_out:
                    f_out.write(output_text)
            except Exception as e:
                print(f"出力ファイル書き込みエラー: {str(e)}", file=sys.stderr)
                sys.exit(1)
        else:
            print(output_text)
    except Exception as e:
        print(f"予期しないエラー: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
