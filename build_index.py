import os
import re

# --- ここにチャプターの開始番号を登録します ---
# 例: 1番から1章、341番から13章、369番から14章...
CHAPTER_MAP = {
    1: "第1章：基本動詞",
    341: "第13章：抽象概念",
    369: "第14章：人間関係"
}

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def generate_index():
    word_dir = "data"
    if not os.path.exists(word_dir): os.makedirs(word_dir)

    words = []
    for filename in os.listdir(word_dir):
        if filename.endswith(".html"):
            display_name = filename.replace(".html", "")
            # ファイル名の先頭の数字だけを抜き出す (例: "341-2" -> 341)
            num_match = re.match(r'^(\d+)', display_name)
            base_num = int(num_match.group(1)) if num_match else 0
            
            words.append({
                "base_num": base_num, # 章判定用
                "sort_id": display_name.split("-")[0] if "-" in display_name else display_name,
                "full_id": display_name.split("-")[0] + ("-" + display_name.split("-")[1] if "-" in display_name and display_name.split("-")[1].isdigit() else ""),
                "display": display_name.replace("-", " "),
                "filename": filename
            })

    # 番号順にソート
    words.sort(key=lambda x: natural_sort_key(x["filename"]))

    # HTMLの組み立て
    html_top = """(前回のindex.htmlの<ul id="wordList">まで)""" 
    # ※実際にはここに前回のHTMLのヘッダー部分を入れます

    list_html = ""
    current_chapter_num = -1
    
    # 章の開始番号を大きい順に並べたリスト（判定用）
    thresholds = sorted(CHAPTER_MAP.keys(), reverse=True)

    for word in words:
        # 今の単語がどの章に属するか判定
        chapter_title = ""
        for t in thresholds:
            if word["base_num"] >= t:
                if t != current_chapter_num:
                    chapter_title = f'<li class="chapter-header">{CHAPTER_MAP[t]}</li>'
                    current_chapter_num = t
                break
        
        list_html += chapter_title
        is_sub = "-" in word["filename"].replace(".html", "")
        item_class = "word-item sub-word" if is_sub else "word-item"
        list_html += f'<li class="{item_class}"><a href="data/{word["filename"]}"><span class="word-id">{word["filename"].replace(".html", "")}</span><span class="word-name">{word["display"]}</span></a></li>\n'

    # 最終的な書き出し（前回のindex.htmlの構成に合わせる）
    # ... (ファイルの保存処理)
