import json
import os
import re
from pathlib import Path
import glob

# メイン単語用のHTMLテンプレート
HTML_TEMPLATE_MAIN = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{number} {word} - English Vocabulary Note</title>
    <style>
        :root {{ --primary-color: #2c3e50; --accent-color: #f4f7f6; --text-main: #333; --text-sub: #666; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.7; color: var(--text-main); max-width: 700px; margin: 0 auto; padding: 30px 20px; background-color: #f0f2f5; }}
        .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        
        /* ナビゲーション */
        .nav-buttons {{ display: flex; justify-content: space-between; margin-bottom: 20px; gap: 10px; }}
        .nav-button {{ flex: 1; padding: 12px 20px; border: 2px solid var(--primary-color); background: white; color: var(--primary-color); text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; transition: 0.3s; cursor: pointer; }}
        .nav-button:hover:not(.disabled) {{ background: var(--primary-color); color: white; }}
        .nav-button.disabled {{ opacity: 0.3; cursor: not-allowed; border-color: #ccc; color: #ccc; }}
        
        /* ヘッダー部分 */
        .back-link {{ display: inline-block; margin-bottom: 25px; text-decoration: none; color: var(--primary-color); font-weight: bold; }}
        .word-header {{ border-bottom: 3px solid var(--primary-color); padding-bottom: 15px; margin-bottom: 25px; }}
        .word-number {{ font-size: 1rem; color: var(--text-sub); font-weight: bold; }}
        .word-title {{ font-size: 3rem; margin: 5px 0; letter-spacing: 1px; }}
        .pos-tag {{ display: inline-block; background: var(--primary-color); color: white; padding: 2px 12px; border-radius: 20px; font-size: 0.85rem; vertical-align: middle; margin-left: 10px; }}

        /* コンテンツ部分 */
        .section-title {{ font-size: 1.1rem; font-weight: bold; color: var(--primary-color); margin-top: 25px; margin-bottom: 10px; display: flex; align-items: center; }}
        .section-title::before {{ content: ""; display: inline-block; width: 4px; height: 18px; background: var(--primary-color); margin-right: 10px; border-radius: 2px; }}
        
        .meaning-jp {{ font-size: 1.5rem; font-weight: bold; background: linear-gradient(transparent 70%, #ffecb3 70%); display: inline-block; margin-bottom: 10px; }}
        .nuance-box {{ background: var(--accent-color); padding: 15px; border-radius: 8px; font-size: 0.95rem; border: 1px dashed var(--primary-color); }}

        /* 例文 */
        .example-item {{ margin-bottom: 15px; padding-left: 15px; border-left: 3px solid #ddd; }}
        .en {{ display: block; font-weight: 500; color: #444; }}
        .ja {{ display: block; color: var(--text-sub); font-size: 0.9rem; }}

        /* リスト */
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .info-item {{ background: #f8f9fa; padding: 12px; border-radius: 8px; font-size: 0.9rem; }}
        .info-label {{ display: block; font-weight: bold; color: var(--text-sub); font-size: 0.8rem; text-transform: uppercase; margin-bottom: 5px; }}
        .list-unit {{ margin-bottom: 4px; border-bottom: 1px solid #eee; padding-bottom: 2px; }}
        .list-unit:last-child {{ border-bottom: none; }}
        .word-small {{ font-weight: bold; color: #444; }}
        .trans-small {{ color: var(--text-sub); font-size: 0.85em; margin-left: 5px; }}

        @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} .word-title {{ font-size: 2.2rem; }} }}
    </style>
</head>
<body>

    <a href="../index.html" class="back-link">← 一覧へ戻る</a>

    <div class="nav-buttons">
        {prev_button}
        {next_button}
    </div>

    <div class="card">
        <div class="word-header">
            <span class="word-number"># {number}</span>
            <h1 class="word-title">{word} <span class="pos-tag">{pos}</span></h1>
        </div>

        <div class="section-title">主な意味</div>
        <div class="meaning-jp">{meaning}</div>
        <div class="nuance-box">
            <strong>ニュアンス：</strong> {nuance}
        </div>

{examples_sections}

        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">語源</span>
                {etymology}
            </div>
            <div class="info-item">
                <span class="info-label">類義語 (Synonyms)</span>
{synonyms}
            </div>
            <div class="info-item">
                <span class="info-label">対義語 (Antonyms)</span>
{antonyms}
            </div>
            <div class="info-item">
                <span class="info-label">関連語</span>
{related}
            </div>
        </div>
    </div>

</body>
</html>"""

# サブ単語用のHTMLテンプレート
HTML_TEMPLATE_SUB = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{number} {word} - English Vocabulary Note</title>
    <style>
        :root {{ --primary-color: #28a745; --accent-color: #f4faf6; --text-main: #333; --text-sub: #666; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.7; color: var(--text-main); max-width: 700px; margin: 0 auto; padding: 30px 20px; background-color: #f0f2f5; }}
        .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        
        /* ナビゲーション */
        .nav-buttons {{ display: flex; justify-content: space-between; margin-bottom: 20px; gap: 10px; }}
        .nav-button {{ flex: 1; padding: 12px 20px; border: 2px solid var(--primary-color); background: white; color: var(--primary-color); text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; transition: 0.3s; cursor: pointer; }}
        .nav-button:hover:not(.disabled) {{ background: var(--primary-color); color: white; }}
        .nav-button.disabled {{ opacity: 0.3; cursor: not-allowed; border-color: #ccc; color: #ccc; }}
        
        /* ヘッダー部分 */
        .back-link {{ display: inline-block; margin-bottom: 25px; text-decoration: none; color: var(--primary-color); font-weight: bold; }}
        .word-header {{ border-bottom: 3px solid var(--primary-color); padding-bottom: 15px; margin-bottom: 25px; }}
        .word-number {{ font-size: 1rem; color: var(--text-sub); font-weight: bold; }}
        .word-title {{ font-size: 3rem; margin: 5px 0; letter-spacing: 1px; }}
        .pos-tag {{ display: inline-block; background: var(--primary-color); color: white; padding: 2px 12px; border-radius: 20px; font-size: 0.85rem; vertical-align: middle; margin-left: 10px; }}

        /* コンテンツ部分 */
        .section-title {{ font-size: 1.1rem; font-weight: bold; color: var(--primary-color); margin-top: 25px; margin-bottom: 10px; display: flex; align-items: center; }}
        .section-title::before {{ content: ""; display: inline-block; width: 4px; height: 18px; background: var(--primary-color); margin-right: 10px; border-radius: 2px; }}
        
        .meaning-jp {{ font-size: 1.5rem; font-weight: bold; background: linear-gradient(transparent 70%, #d4edda 70%); display: inline-block; margin-bottom: 10px; }}
        .nuance-box {{ background: var(--accent-color); padding: 15px; border-radius: 8px; font-size: 0.95rem; border: 1px dashed var(--primary-color); }}

        /* 例文 */
        .example-item {{ margin-bottom: 15px; padding-left: 15px; border-left: 3px solid #ddd; }}
        .en {{ display: block; font-weight: 500; color: #444; }}
        .ja {{ display: block; color: var(--text-sub); font-size: 0.9rem; }}

        /* リスト */
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .info-item {{ background: #f8f9fa; padding: 12px; border-radius: 8px; font-size: 0.9rem; }}
        .info-label {{ display: block; font-weight: bold; color: var(--text-sub); font-size: 0.8rem; text-transform: uppercase; margin-bottom: 5px; }}
        .list-unit {{ margin-bottom: 4px; border-bottom: 1px solid #eee; padding-bottom: 2px; }}
        .list-unit:last-child {{ border-bottom: none; }}
        .word-small {{ font-weight: bold; color: #444; }}
        .trans-small {{ color: var(--text-sub); font-size: 0.85em; margin-left: 5px; }}

        @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} .word-title {{ font-size: 2.2rem; }} }}
    </style>
</head>
<body>

    <a href="../index.html" class="back-link">← 一覧へ戻る</a>

    <div class="nav-buttons">
        {prev_button}
        {next_button}
    </div>

    <div class="card">
        <div class="word-header">
            <span class="word-number"># {number} (関連語)</span>
            <h1 class="word-title">{word} <span class="pos-tag">{pos}</span></h1>
        </div>

        <div class="section-title">意味</div>
        <div class="meaning-jp">{meaning}</div>
        <div class="nuance-box">
            <strong>ニュアンス：</strong> {nuance}
        </div>

{examples_sections}

        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">語源</span>
                {etymology}
            </div>
            <div class="info-item">
                <span class="info-label">類義語 (Synonyms)</span>
{synonyms}
            </div>
            <div class="info-item">
                <span class="info-label">対義語 (Antonyms)</span>
{antonyms}
            </div>
            <div class="info-item">
                <span class="info-label">関連語</span>
{related}
            </div>
        </div>
    </div>

</body>
</html>"""


def load_all_vocabulary_data():
    """すべてのJSONファイルを読み込んで統合"""
    all_words = []
    
    # vocabulary_data.json が存在する場合（従来の単一ファイル）
    if os.path.exists('vocabulary_data.json'):
        print("📖 vocabulary_data.json を読み込んでいます...")
        with open('vocabulary_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_words.extend(data.get('words', []))
    
    # vocabulary_data/ フォルダ内のJSONファイルを読み込み（新しい分割方式）
    if os.path.exists('vocabulary_data'):
        json_files = sorted(glob.glob('vocabulary_data/*.json'))
        for json_file in json_files:
            print(f"📖 {json_file} を読み込んでいます...")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_words.extend(data.get('words', []))
    
    if not all_words:
        print("⚠️  単語データが見つかりません！")
        print("   vocabulary_data.json または vocabulary_data/*.json を確認してください。")
    
    return all_words


def parse_number(number_str):
    """番号文字列をパース (例: "422" -> (422, 0), "422-2" -> (422, 2))"""
    parts = str(number_str).split('-')
    main_num = int(parts[0])
    sub_num = int(parts[1]) if len(parts) > 1 else 0
    return (main_num, sub_num)


def sort_words_by_number(words):
    """単語をメイン→サブの順番でソート"""
    return sorted(words, key=lambda w: parse_number(w['number']))


def get_filename(word_data):
    """ファイル名を生成"""
    number = str(word_data['number'])
    word = word_data['word']
    return f"{number}-{word}.html"


def generate_nav_buttons(current_index, sorted_words):
    """ナビゲーションボタンを生成"""
    # 前の単語
    if current_index > 0:
        prev_word = sorted_words[current_index - 1]
        prev_filename = get_filename(prev_word)
        prev_button = f'<a href="{prev_filename}" class="nav-button">← 前の単語</a>'
    else:
        prev_button = '<span class="nav-button disabled">← 前の単語</span>'
    
    # 次の単語
    if current_index < len(sorted_words) - 1:
        next_word = sorted_words[current_index + 1]
        next_filename = get_filename(next_word)
        next_button = f'<a href="{next_filename}" class="nav-button">次の単語 →</a>'
    else:
        next_button = '<span class="nav-button disabled">次の単語 →</span>'
    
    return prev_button, next_button


def generate_example_section(section_title, examples):
    """例文セクションを生成"""
    html = f'        <div class="section-title">{section_title}</div>\n'
    for ex in examples:
        en = ex['en'].replace(ex.get('highlight', ''), f"<strong>{ex.get('highlight', '')}</strong>")
        html += f'''        <div class="example-item">
            <span class="en">{en}</span>
            <span class="ja">{ex['ja']}</span>
        </div>\n'''
    return html


def generate_word_list(words, is_sub_word=False, main_number=None):
    """単語リストを生成（サブ単語の場合はリンク付き）"""
    html = ""
    for w in words:
        if 'link' in w and w['link']:
            color = '#28a745' if is_sub_word else '#2c3e50'
            html += f'''                <a href="{w['link']}" style="text-decoration: none;">
                    <span class="word-small" style="color: {color};">{w["word"]}</span>
                    <span class="trans-small">({w["trans"]})</span>
                </a>\n'''
        else:
            html += f'                <div class="list-unit"><span class="word-small">{w["word"]}</span><span class="trans-small">({w["trans"]})</span></div>\n'
    return html


def generate_html(data, current_index, sorted_words):
    """JSONデータからHTMLを生成"""
    is_sub_word = '-' in str(data['number'])
    template = HTML_TEMPLATE_SUB if is_sub_word else HTML_TEMPLATE_MAIN
    
    prev_button, next_button = generate_nav_buttons(current_index, sorted_words)
    main_number = str(data['number']).split('-')[0] if is_sub_word else None
    
    examples_sections = ""
    if 'example_sections' in data:
        for section in data['example_sections']:
            examples_sections += generate_example_section(section['title'], section['examples'])
    else:
        examples_sections = generate_example_section('例文', data.get('examples', []))
    
    synonyms = generate_word_list(data.get('synonyms', []), is_sub_word, main_number)
    antonyms = generate_word_list(data.get('antonyms', []), is_sub_word, main_number)
    related = generate_word_list(data.get('related', []), is_sub_word, main_number)
    
    html = template.format(
        number=data['number'],
        word=data['word'],
        pos=data['pos'],
        meaning=data['meaning'],
        nuance=data['nuance'],
        examples_sections=examples_sections,
        etymology=data['etymology'],
        synonyms=synonyms,
        antonyms=antonyms,
        related=related,
        prev_button=prev_button,
        next_button=next_button
    )
    
    return html


def main():
    """メイン処理"""
    # すべてのJSONファイルから単語データを読み込み
    all_words = load_all_vocabulary_data()
    
    if not all_words:
        return
    
    # 単語をソート（メイン→サブの順）
    sorted_words = sort_words_by_number(all_words)
    
    # dataディレクトリを作成
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # 各単語のHTMLファイルを生成
    for index, word_data in enumerate(sorted_words):
        html_content = generate_html(word_data, index, sorted_words)
        
        filename = get_filename(word_data)
        filepath = data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        word_type = "サブ単語" if '-' in str(word_data['number']) else "メイン単語"
        print(f"✓ 生成完了 [{word_type}]: {filepath}")
    
    print(f"\n合計 {len(sorted_words)} 件のHTMLファイルを生成しました。")


if __name__ == '__main__':
    main()
