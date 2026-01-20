import os
import re

# ==========================================
# 1. チャプターの設定
# ==========================================
# キー(数字)は「その章が始まる単語番号」です。
# 番号順に並んだ際、この数字以上の単語が現れると見出しが挿入されます。
CHAPTER_MAP = {
    1: "第1章：基本動詞",
    341: "第13章：抽象概念",
    369: "第14章：人間関係"
}

# ==========================================
# 2. 補助関数
# ==========================================
def natural_sort_key(s):
    """'341-2' を [341, 2] に変換して正しくソートする"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_base_number(filename):
    """ファイル名から先頭の数字(341など)を取得する"""
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else 0

# ==========================================
# 3. メイン処理
# ==========================================
def generate_index():
    word_dir = "data"
    if not os.path.exists(word_dir):
        os.makedirs(word_dir)

    # 単語ファイルの取得とソート
    files = [f for f in os.listdir(word_dir) if f.endswith(".html")]
    files.sort(key=natural_sort_key)

    # HTMLのヘッダー部分（CSS含む）
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My English Dictionary</title>
    <style>
        :root { --primary-color: #007bff; --chapter-color: #6c757d; --bg-color: #f4f7f9; }
        body { font-family: sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { width: 100%; max-width: 800px; }
        h1 { color: var(--primary-color); text-align: center; border-bottom: 3px solid var(--primary-color); padding-bottom: 10px; }
        .search-box { width: 100%; padding: 15px; font-size: 18px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 20px; box-sizing: border-box; }
        .word-list { list-style: none; padding: 0; }
        
        /* 章の見出し */
        .chapter-header { background: var(--chapter-color); color: white; padding: 10px 15px; margin: 30px 0 10px 0; border-radius: 5px; font-weight: bold; }
        
        /* 単語アイテム */
        .word-item { background: white; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .word-item a { display: flex; padding: 12px 20px; text-decoration: none; color: #333; align-items: center; }
        .word-id { font-weight: bold; color: var(--primary-color); min-width: 70px; font-family: monospace; }
        .word-name { font-size: 1.1em; }
        
        /* 関連語（枝番あり）のスタイル */
        .sub-word { margin-left: 30px; border-left: 4px solid #ccd5ae; background-color: #fafafa; }
        .sub-word .word-id { color: #6a994e; }
    </style>
</head>
<body>
<div class="container">
    <h1>英単語辞書 データベース</h1>
    <input type="text" id="searchInput" class="search-box" placeholder="単語・番号で検索..." onkeyup="filterList()">
    <ul class="word-list" id="wordList">
"""

    # リスト部分の生成
    current_chapter_start = -1
    # 章の開始番号を降順（大きい順）に並べたリスト
    sorted_chapter_starts = sorted(CHAPTER_MAP.keys(), reverse=True)

    for filename in files:
        base_num = get_base_number(filename)
        
        # 章見出しの挿入判定
        for start_num in sorted_chapter_starts:
            if base_num >= start_num:
                if start_num != current_chapter_start:
                    html_content += f'        <li class="chapter-header">{CHAPTER_MAP[start_num]}</li>\n'
                    current_chapter_start = start_num
                break

        # 単語アイテムの生成
        word_id = filename.replace(".html", "")
        # 表示名から数字を除去して綺麗にする（例: "341-impotence" -> "impotence"）
        display_name = re.sub(r'^[0-9-]+', '', word_id).replace("-", " ").strip()
        
        is_sub = "-" in word_id and word_id.split("-")[1].isdigit()
        item_class = "word-item sub-word" if is_sub else "word-item"

        html_content += f'        <li class="{item_class}"><a href="data/{filename}">'
        html_content += f'<span class="word-id">{word_id.split("-")[0] + ("-" + word_id.split("-")[1] if is_sub else "")}</span>'
        html_content += f'<span class="word-name">{display_name}</span></a></li>\n'

    # フッター部分（JavaScript含む）
    html_content += """    </ul>
</div>
<script>
    function filterList() {
        const input = document.getElementById('searchInput');
        const filter = input.value.toLowerCase();
        const li = document.getElementById("wordList").getElementsByTagName('li');
        for (let i = 0; i < li.length; i++) {
            if (li[i].classList.contains('chapter-header')) continue; // 章見出しは無視
            const text = li[i].textContent || li[i].innerText;
            li[i].style.display = text.toLowerCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
</script>
</body>
</html>"""

    # 書き出し
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully updated index.html with {len(files)} words.")

if __name__ == "__main__":
    generate_index()
