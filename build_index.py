import os
import re

# ==========================================
# 1. チャプターの設定
# ==========================================
CHAPTER_MAP = {
    1: "【速読英単語】第1章：人間と動物の違い",
    341: "【速読英単語】第13章：暴力はなぜ起きる",
    369: "【速読英単語】第14章：謙虚さが教えてくれること⑴",
    403: "【速読英単語】第15章：謙虚さが教えてくれること⑵",
    424: "【速読英単語】第16章：謙虚さが教えてくれること⑶",
    441: "【速読英単語】第17章：人種差別を排除するには⑴",
    473: "【速読英単語】第18章：人種差別を排除するには⑵",
    502: "【速読英単語】第19章：受刑者に対する実験の是非⑴",
    523: "【速読英単語】第20章：受刑者に対する実験の是非⑵",
    558: "【速読英単語】第21章：ホーソン効果",
    579: "【速読英単語】第22章：ジャンクフードから見る経済格差⑴",
    594: "【速読英単語】第23章：ジャンクフードから見る経済格差⑵",
    617: "【速読英単語】第24章：ジャンクフードから見る経済格差⑶",
    629: "【速読英単語】第25章：ジャンクフードから見る経済格差⑷",
    646: "【速読英単語】第26章：適切な塩の摂取量とは⑴",
    671: "【速読英単語】第27章：適切な塩の摂取量とは⑵",
    700: "【速読英単語】第28章：健康によい運動量の本当の目安⑴",
    732: "【速読英単語】第29章：健康によい運動量の本当の目安⑵",
    743: "【速読英単語】第30章：健康によい運動量の本当の目安⑶",
    763: "【速読英単語】第31章：プラスチックが健康に与える影響⑴",
    790: "【速読英単語】第32章：プラスチックが健康に与える影響⑵",
    826: "【速読英単語】第33章：プラスチックが健康に与える影響⑶",
    4374: "【東進上級英単語1000】ステージ5",
    4474: "【東進上級英単語1000】ステージ6",
    4574: "【東進上級英単語1000】ステージ7",
    4674: "【東進上級英単語1000】ステージ8",
    4774: "【東進上級英単語1000】ステージ9",
    4874: "【東進上級英単語1000】ステージ10"
}

# ==========================================
# 2. 補助関数
# ==========================================
def natural_sort_key(filename):
    parts = re.split(r'(\d+)', filename)
    converted_parts = [int(p) if p.isdigit() else p.lower() for p in parts if p]
    if len(converted_parts) > 1:
        if converted_parts[1] == '.html':
            return [converted_parts[0], 0] + converted_parts[2:]
        else:
            return [converted_parts[0], 1] + converted_parts[2:]
    return converted_parts

def get_base_number(filename):
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else 0

# ==========================================
# 3. メイン処理
# ==========================================
def generate_index():
    word_dir = "data"
    if not os.path.exists(word_dir):
        os.makedirs(word_dir)

    files = [f for f in os.listdir(word_dir) if f.endswith(".html")]
    files.sort(key=natural_sort_key)

    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>English Dictionary</title>
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
        
        .word-item.hidden { display: none; }
        .loading-indicator { text-align: center; padding: 20px; color: var(--chapter-color); }
    </style>
</head>
<body>
<div class="container">
    <h1>英単語辞書 データベース</h1>
    <nav class="toc">
        <div class="toc-title">Chapter Index</div>
        <ul class="toc-links">
"""

    for s_num in sorted(CHAPTER_MAP.keys()):
        html_content += f'            <li><a href="#chapter-{s_num}">{CHAPTER_MAP[s_num]}</a></li>\n'
    
    html_content += """        </ul>
    </nav>
    <input type="text" id="searchInput" class="search-box" placeholder="単語・番号で検索..." onkeyup="filterList()">
    <ul class="word-list" id="wordList">
"""

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
        display_name = re.sub(r'^[0-9-]+', '', word_id_full).replace("-", " ").strip()
        parts = word_id_full.split("-")
        is_sub = len(parts) > 1 and parts[1].isdigit()
        item_class = "word-item sub-word" if is_sub else "word-item"
        display_id = parts[0] + ("-" + parts[1] if is_sub else "")

        html_content += f'        <li class="{item_class}"><a href="data/{filename}">'
        html_content += f'<span class="word-id">{display_id}</span>'
        html_content += f'<span class="word-name">{display_name}</span></a></li>\n'

    html_content += """    </ul>
    <div class="loading-indicator" id="loadingIndicator">スクロールして読み込み...</div>
</div>
<script>
    // --- 座標ベースのLazy Loading改良版 ---
    const wordList = document.getElementById('wordList');
    const allItems = Array.from(wordList.children).filter(item => item.classList.contains('word-item'));
    const margin = 1200; // 画面外1200px先まで事前に表示させる

    // 現在の表示位置をチェックしてhiddenを外す
    function checkVisibleItems() {
        const triggerLimit = window.innerHeight + window.scrollY + margin;
        
        let hasHidden = false;
        for (let item of allItems) {
            if (item.classList.contains('hidden')) {
                // hidden状態だとgetBoundingClientRect().topが正確に取れない場合があるため、
                // 親要素内でのオフセット等を利用するか、単純に順番にチェックします。
                if (item.offsetTop < triggerLimit) {
                    item.classList.remove('hidden');
                } else {
                    hasHidden = true;
                    break; // これ以降はまだ画面より遠いので中断
                }
            }
        }
        
        document.getElementById('loadingIndicator').style.display = hasHidden ? 'block' : 'none';
    }

    // 初期化
    function initializeLazyLoad() {
        allItems.forEach(item => item.classList.add('hidden'));
        checkVisibleItems();
    }

    // 章ジャンプ
    function loadChapterAndScroll(event, chapterId) {
        event.preventDefault();
        const chapterHeader = document.getElementById(chapterId);
        if (!chapterHeader) return;

        // ジャンプ先の直後の要素をいくつか強制表示（スクロール時の空白防止）
        let nextEl = chapterHeader.nextElementSibling;
        for (let i = 0; i < 40 && nextEl; i++) {
            if (nextEl.classList.contains('word-item')) nextEl.classList.remove('hidden');
            nextEl = nextEl.nextElementSibling;
        }

        chapterHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // スクロール中・完了後に位置判定を再実行
        setTimeout(checkVisibleItems, 100);
        setTimeout(checkVisibleItems, 600);
    }

    // イベント登録
    window.addEventListener('scroll', () => {
        window.requestAnimationFrame(checkVisibleItems);
    });

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.toc-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                const chapterId = link.getAttribute('href').substring(1);
                loadChapterAndScroll(e, chapterId);
            });
        });
        initializeLazyLoad();
    });

    // 検索機能
    function filterList() {
        const filter = document.getElementById('searchInput').value.toLowerCase();
        const listItems = wordList.getElementsByTagName('li');

        for (let item of listItems) {
            if (item.classList.contains('chapter-header')) {
                item.style.display = filter === "" ? "" : "none";
                continue;
            }
            
            if (filter === "") {
                item.classList.add('hidden');
                item.style.display = "";
            } else {
                const text = item.textContent || item.innerText;
                item.classList.remove('hidden');
                item.style.display = text.toLowerCase().includes(filter) ? "" : "none";
            }
        }
        if (filter === "") checkVisibleItems();
    }
</script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Update Complete: index.html has been rebuilt with {len(files)} words (Smart Coordinate Loading enabled).")

if __name__ == "__main__":
    generate_index()
