import os
import re

# ==========================================
# 1. チャプターの設定
# ==========================================
# 規則性がない場合も、ここに「開始番号: 章タイトル」を足すだけでOKです。
CHAPTER_MAP = {
    1: "第1章：人間と動物の違い",
    341: "第13章：暴力はなぜ起きる",
    369: "第14章：謙虚さが教えてくれること⑴",
    403: "第15章：謙虚さが教えてくれること⑵"
}

# ==========================================
# 2. 補助関数
# ==========================================
def natural_sort_key(s):
    """'341-2' などを数値として正しく並び替える"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_base_number(filename):
    """ファイル名(341-impotence.html)の先頭数字を取得"""
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

    # --- HTMLヘッダーとCSS定義 ---
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
        h1 { color: var(--primary-color); text-align: center; border-bottom: 3px solid var(--primary-color); padding-bottom: 10px; margin-bottom: 20px; }
        
        /* 目次（ナビゲーション） */
        .toc { background: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .toc-title { font-size: 0.85rem; font-weight: bold; color: var(--chapter-color); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .toc-links { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 0; }
        .toc-links a { text-decoration: none; color: var(--primary-color); font-size: 0.85rem; background: #eef2f7; padding: 6px 12px; border-radius: 20px; transition: 0.2s; }
        .toc-links a:hover { background: var(--primary-color); color: white; }

        .search-box { width: 100%; padding: 15px; font-size: 18px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 20px; box-sizing: border-box; outline: none; }
        .search-box:focus { border-color: var(--primary-color); }
        
        /* リストと見出し */
        .word-list { list-style: none; padding: 0; }
        .chapter-header { background: var(--chapter-color); color: white; padding: 10px 15px; margin: 40px 0 12px 0; border-radius: 5px; font-weight: bold; scroll-margin-top: 20px; }
        .word-item { background: white; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: 0.2s; }
        .word-item:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .word-item a { display: flex; padding: 12px 20px; text-decoration: none; color: #333; align-items: center; }
        .word-id { font-weight: bold; color: var(--primary-color); min-width: 75px; font-family: monospace; }
        .word-name { font-size: 1.1em; font-weight: 500; }
        
        /* 関連語（枝番あり） */
        .sub-word { margin-left: 30px; border-left: 4px solid #ccd5ae; background-color: #fafafa; }
        .sub-word .word-id { color: #6a994e; }
    </style>
</head>
<body>
<div class="container">
    <h1>英単語辞書 データベース</h1>
"""

    # --- 目次セクションの自動生成 ---
    html_content += '    <nav class="toc">\n        <div class="toc-title">Chapter Index</div>\n        <ul class="toc-links">\n'
    for s_num in sorted(CHAPTER_MAP.keys()):
        html_content += f'            <li><a href="#chapter-{s_num}">{CHAPTER_MAP[s_num]}</a></li>\n'
    html_content += '        </ul>\n    </nav>\n'

    # 検索ボックスとリスト開始
    html_content += """    <input type="text" id="searchInput" class="search-box" placeholder="単語・番号で検索..." onkeyup="filterList()">
    <ul class="word-list" id="wordList">
"""

    # --- 単語リスト部分の生成 ---
    current_chapter_start = -1
    sorted_thresholds = sorted(CHAPTER_MAP.keys(), reverse=True)

    for filename in files:
        base_num = get_base_number(filename)
        
        # 章見出しの挿入
        for t in sorted_thresholds:
            if base_num >= t:
                if t != current_chapter_start:
                    html_content += f'        <li class="chapter-header" id="chapter-{t}">{CHAPTER_MAP[t]}</li>\n'
                    current_chapter_start = t
                break

        # IDと表示名の整理
        word_id_full = filename.replace(".html", "")
        # 表示用：341-impotence -> impotence
        display_name = re.sub(r'^[0-9-]+', '', word_id_full).replace("-", " ").strip()
        
        # 枝番チェック (例: 341-2)
        is_sub = "-" in word_id_full and word_id_full.split("-")[1].isdigit()
        item_class = "word-item sub-word" if is_sub else "word-item"

        # リスト行の組み立て
        # ID表示用：341-2-impotent -> 341-2
        id_parts = word_id_full.split("-")
        display_id = id_parts[0] + ("-" + id_parts[1] if is_sub else "")

        html_content += f'        <li class="{item_class}"><a href="data/{filename}">'
        html_content += f'<span class="word-id">{display_id}</span>'
        html_content += f'<span class="word-name">{display_name}</span></a></li>\n'

    # --- フッターと検索スクリプト ---
    html_content += """    </ul>
</div>
<script>
    function filterList() {
        const input = document.getElementById('searchInput');
        const filter = input.value.toLowerCase();
        const items = document.getElementById("wordList").getElementsByTagName('li');
        
        for (let i = 0; i < items.length; i++) {
            // 章見出しは検索対象外だが、検索中は邪魔なので隠す
            if (items[i].classList.contains('chapter-header')) {
                items[i].style.display = filter === "" ? "" : "none";
                continue;
            }
            const text = items[i].textContent || items[i].innerText;
            items[i].style.display = text.toLowerCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
</script>
</body>
</html>"""

    # ファイル書き出し
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Update Complete: index.html has been rebuilt with {len(files)} words.")

if __name__ == "__main__":
    generate_index()
