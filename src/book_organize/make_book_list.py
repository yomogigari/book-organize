#!/usr/bin/env python
# coding: utf-8
"""電子書籍ファイル名から作者名と分類情報を生成する。"""
import os
import sys
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
    # 歴史的仮名遣い → 基本形
    'ヰ': 'イ', 'ヱ': 'エ',
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
    """文字列がすべてカタカナとして扱える文字で構成されているか確認する。"""
    return all(unicodedata.name(ch, "").startswith("KATAKANA") for ch in text)


def is_complete_katakana_reading(text: str) -> bool:
    """読みが空でなく、未変換文字を含まないカタカナだけか確認する。"""
    return bool(text) and is_katakana(text)

def build_group_string(kana_text: str, raw_kana: str) -> str:
    """カタカナ表記の先頭2文字を50音の行へ置き換えて連結する。"""
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

def build_book_list_rows(target_dir, short=False, reading_dict=None):
    """対象ディレクトリを走査し、従来CSVと同じ内容の行を返す。"""
    if not os.path.isdir(target_dir):
        raise NotADirectoryError(f"指定されたディレクトリ '{target_dir}' は存在しません。")

    files = os.listdir(target_dir)

    target_files = []
    for f in files:
        _, ext = os.path.splitext(f)
        if ext.lower() in TARGET_EXTENSIONS:
            target_files.append(f)

    sudachi_cache = {}
    names_to_process = set()
    file_info_list = []
    for f in target_files:
        extracted = extract_name(f)
        file_info_list.append((extracted, f))
        if extracted != "!!":
            names_to_process.add(extracted)

    reading_dict = reading_dict or {}
    names_for_sudachi = names_to_process.difference(reading_dict)

    for name in names_to_process:
        if name in reading_dict:
            raw_kana = reading_dict[name]
            sudachi_cache[name] = (raw_kana, normalize_katakana(raw_kana))

    if names_for_sudachi:
        sudachi_tokenizer = dictionary.Dictionary(dict="full").create()
        mode = tokenizer.Tokenizer.SplitMode.C

        for name in names_for_sudachi:
            try:
                tokens = sudachi_tokenizer.tokenize(name, mode)
                raw_kana = "".join(token.reading_form() for token in tokens)
            except Exception as e:
                print(f"Sudachi解析エラー '{name}': {str(e)}", file=sys.stderr)
                raw_kana = ""
            normalized_kana = normalize_katakana(raw_kana)
            sudachi_cache[name] = (raw_kana, normalized_kana)

    output_rows = []
    for extracted, fname in file_info_list:
        if extracted != "!!":
            raw_kana, normalized_kana = sudachi_cache.get(extracted, ("", ""))
        else:
            raw_kana, normalized_kana = ("!!", "!!")
        head2 = normalized_kana[:2]
        if is_complete_katakana_reading(normalized_kana):
            group_str = build_group_string(normalized_kana, raw_kana)
            if group_str and not is_katakana(group_str):
                group_str = "!!"
        else:
            group_str = "!!"

        if short:
            row = [group_str, fname]
        else:
            row = [group_str, head2, normalized_kana, raw_kana, extracted, fname]
        output_rows.append(row)

    if short:
        output_rows.sort(key=lambda x: (x[0], x[1]))
    else:
        output_rows.sort(key=lambda x: (x[0], x[5]))
    return output_rows


def format_csv_rows(rows):
    """分類行を従来形式のCSV文字列へ変換する。"""
    output_lines = []
    for row in rows:
        escaped_row = [escape_csv_field(field) for field in row]
        output_lines.append(",".join(escaped_row))
    return "\n".join(output_lines)


def write_csv_rows(rows, output_path=None):
    """分類行をファイルへ保存するか、標準出力へ出力する。"""
    output_text = format_csv_rows(rows)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(output_text)
    else:
        print(output_text)
