import os
import re

# ==========================================
# 1. チャプターの設定
# ==========================================
CHAPTER_MAP = {
    1: "第1章：人間と動物の違い",
    341: "第13章：暴力はなぜ起きる",
    369: "第14章：謙虚さが教えてくれること⑴",
    403: "第15章：謙虚さが教えてくれること⑵",
    424: "第16章：謙虚さが教えてくれること⑶",
    441: "第17章：人種差別を排除するには⑴",
    473: "第18章：人種差別を排除するには⑵",
    502: "第19章：受刑者に対する実験の是非⑴"
}

# ==========================================
# 2. 補助関数（ソートロジックの改良）
# ==========================================
def natural_sort_key(filename):
    """
    369.html, 369-2.html, 370.html を正しく並べるためのキー
    順序: 369 -> 369-2 -> 369-3 -> 370
    """
    # 数字とそれ以外に分解
    parts = re.split(r'(\d+)', filename)
    
    # 数値化できる部分は数値に、それ以外は小文字にする
    converted_parts = [int(p) if p.isdigit() else p.lower() for p in parts if p]
    
    # 重要：枝番がない(369.html) を 枝番がある(369-2.html) より前に持ってくるための処理
    # converted_parts[0] が 369、converted_parts[1] が "." か "-" になる
    if len(converted_parts) > 1:
        # 2番目の要素がハイフンでなければ、枝番なしと判断してソート順を繰り上げる
        if converted_parts[1] == '.html':
            return [converted_parts[0], 0] + converted_parts[2:]
        else:
            return [converted_parts[0], 1] + converted_parts[2:]
            
    return converted_parts

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
    # 改良したソートキーを適用
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
        
        .toc { background: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .toc-title { font-size: 0.85rem; font-weight: bold; color: var(--chapter-color); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .toc-links { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 0; }
        .toc-links a { text-decoration: none; color: var(--primary-color); font-size: 0.85rem; background: #eef2f7; padding: 6px 12px; border-radius: 20px; transition: 0.2s; }
        .toc-links a:hover { background: var(--primary-color); color: white; }

        .search-box { width: 100%; padding: 15px; font-size: 18px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 20px; box-sizing: border-box; outline: none; }
        .search-box:focus { border-color: var(--primary-color); }
        
        .word-list { list-style: none; padding: 0; }
        .chapter-header { background: var(--chapter-color); color: white; padding: 10px 15px; margin: 40px 0 12px 0; border-radius: 5px; font-weight: bold; scroll-margin-top: 20px; }
        .word-item { background: white; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: 0.2s; }
        .word-item:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .word-item a { display: flex; padding: 12px 20px; text-decoration: none; color: #333; align-items: center; }
        .word-id { font-weight: bold; color: var(--primary-color); min-width: 75px; font-family: monospace; }
        .word-name { font-size: 1.1em; font-weight: 500; }
        
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

    html_content += """    <input type="text" id="searchInput" class="search-box" placeholder="単語・番号で検索..." onkeyup="filterList()">
    <ul class="word-list" id="wordList">
"""

    # --- 単語リスト部分の生成 ---
    current_chapter_start = -1
    sorted_thresholds = sorted(CHAPTER_MAP.keys(), reverse=True)

    for filename in files:
        base_num = get_base_number(filename)
        
        for t in sorted_thresholds:
            if base_num >= t:
                if t != current_chapter_start:
                    html_content += f'        <li class="chapter-header" id="chapter-{t}">{CHAPTER_MAP[t]}</li>\n'
                    current_chapter_start = t
                break

        word_id_full = filename.replace(".html", "")
        # 表示名のクリーンアップ
        display_name = re.sub(r'^[0-9-]+', '', word_id_full).replace("-", " ").strip()
        
        # 枝番チェック (ハイフンが含まれ、かつその次が数字の場合)
        parts = word_id_full.split("-")
        is_sub = len(parts) > 1 and parts[1].isdigit()
        
        item_class = "word-item sub-word" if is_sub else "word-item"

        # ID表示用の整形
        display_id = parts[0] + ("-" + parts[1] if is_sub else "")

        html_content += f'        <li class="{item_class}"><a href="data/{filename}">'
        html_content += f'<span class="word-id">{display_id}</span>'
        html_content += f'<span class="word-name">{display_name}</span></a></li>\n'

    html_content += """    </ul>
</div>
<script>
    function filterList() {
        const input = document.getElementById('searchInput');
        const filter = input.value.toLowerCase();
        const items = document.getElementById("wordList").getElementsByTagName('li');
        
        for (let i = 0; i < items.length; i++) {
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

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Update Complete: index.html has been rebuilt with {len(files)} words.")

if __name__ == "__main__":
    generate_index()
