import os
import re
import json

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
    return [int(p) if p.isdigit() else p.lower() for p in parts if p]

def get_base_number(filename):
    match = re.match(r'^(\d+)', filename)
    return int(match.group(1)) if match else 0

# ==========================================
# 3. メイン処理
# ==========================================
def generate_index_and_data():
    word_dir = "data"
    if not os.path.exists(word_dir):
        print(f"Error: {word_dir} directory not found.")
        return

    files = [f for f in os.listdir(word_dir) if f.endswith(".html")]
    files.sort(key=natural_sort_key)

    # 1. 単語リスト情報の抽出（JSON用）
    word_db = []
    sorted_thresholds = sorted(CHAPTER_MAP.keys(), reverse=True)
    
    current_chapter_id = None
    for filename in files:
        base_num = get_base_number(filename)
        
        # どの章に属するか判定
        chapter_title = ""
        chapter_id = 0
        for t in sorted_thresholds:
            if base_num >= t:
                chapter_title = CHAPTER_MAP[t]
                chapter_id = t
                break

        word_id_full = filename.replace(".html", "")
        display_name = re.sub(r'^[0-9-]+', '', word_id_full).replace("-", " ").strip()
        parts = word_id_full.split("-")
        is_sub = len(parts) > 1 and parts[1].isdigit()
        display_id = parts[0] + ("-" + parts[1] if is_sub else "")

        word_db.append({
            "id": display_id,
            "name": display_name,
            "file": filename,
            "is_sub": is_sub,
            "chapter_id": chapter_id,
            "chapter_title": chapter_title
        })

    # JSONデータとして書き出し
    with open("word_data.json", "w", encoding="utf-8") as jf:
        json.dump(word_db, jf, ensure_ascii=False, indent=2)

    # 2. index.html の生成
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
        h1 { color: var(--primary-color); text-align: center; border-bottom: 3px solid var(--primary-color); padding-bottom: 10px; }
        
        .toc { background: white; padding: 15px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .toc-links { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; }
        .toc-links a { text-decoration: none; color: var(--primary-color); font-size: 0.8rem; background: #eef2f7; padding: 5px 10px; border-radius: 15px; }

        .search-box { width: 100%; padding: 15px; font-size: 18px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 20px; box-sizing: border-box; }
        
        .word-list { list-style: none; padding: 0; }
        .chapter-header { background: var(--chapter-color); color: white; padding: 10px 15px; margin: 30px 0 10px 0; border-radius: 5px; font-weight: bold; }
        .word-item { background: white; margin-bottom: 8px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); animation: fadeIn 0.3s ease-in; }
        .word-item a { display: flex; padding: 12px 20px; text-decoration: none; color: #333; }
        .word-id { font-weight: bold; color: var(--primary-color); min-width: 75px; }
        .sub-word { margin-left: 25px; border-left: 4px solid #ccd5ae; }
        
        #sentinel { height: 50px; display: flex; align-items: center; justify-content: center; color: #888; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
<div class="container">
    <h1>英単語辞書</h1>
    <nav class="toc"><ul class="toc-links">"""

    for s_num in sorted(CHAPTER_MAP.keys()):
        html_content += f'<li><a href="#" onclick="jumpToChapter({s_num}); return false;">{CHAPTER_MAP[s_num]}</a></li>'

    html_content += """</ul></nav>
    <input type="text" id="searchInput" class="search-box" placeholder="検索..." onkeyup="handleSearch()">
    <ul class="word-list" id="wordList"></ul>
    <div id="sentinel">さらに読み込み中...</div>
</div>

<script>
    let allData = [];
    let filteredData = [];
    let currentIndex = 0;
    const PAGE_SIZE = 40;
    const wordList = document.getElementById('wordList');
    const sentinel = document.getElementById('sentinel');
    let currentChapterInView = null;

    // 1. データの初回取得 (Fetch)
    async function loadInitialData() {
        try {
            const response = await fetch('word_data.json');
            allData = await response.json();
            filteredData = allData;
            initObserver();
        } catch (e) { console.error("データ読み込み失敗", e); }
    }

    // 2. リストへの追加描画
    function renderNextPage() {
        const nextSet = filteredData.slice(currentIndex, currentIndex + PAGE_SIZE);
        nextSet.forEach(word => {
            // 章ヘッダーの挿入
            if (word.chapter_id !== currentChapterInView && !document.getElementById('search-active')) {
                const header = document.createElement('li');
                header.className = 'chapter-header';
                header.id = `chapter-${word.chapter_id}`;
                header.textContent = word.chapter_title;
                wordList.appendChild(header);
                currentChapterInView = word.chapter_id;
            }

            const li = document.createElement('li');
            li.className = word.is_sub ? 'word-item sub-word' : 'word-item';
            li.innerHTML = `<a href="data/${word.file}">
                <span class="word-id">${word.id}</span>
                <span class="word-name">${word.name}</span>
            </a>`;
            wordList.appendChild(li);
        });
        currentIndex += PAGE_SIZE;
        if (currentIndex >= filteredData.length) sentinel.style.display = 'none';
    }

    // 3. Intersection Observer (交差監視)
    function initObserver() {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && currentIndex < filteredData.length) {
                renderNextPage();
            }
        }, { rootMargin: '200px' });
        observer.observe(sentinel);
    }

    // 4. 検索機能
    function handleSearch() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        currentIndex = 0;
        wordList.innerHTML = query ? '<div id="search-active"></div>' : ''; 
        currentChapterInView = null;
        sentinel.style.display = 'block';
        
        filteredData = allData.filter(w => 
            w.name.toLowerCase().includes(query) || w.id.toLowerCase().includes(query)
        );
        renderNextPage();
    }

    // 5. 章へのジャンプ
    function jumpToChapter(id) {
        const query = document.getElementById('searchInput');
        if (query.value) { query.value = ''; handleSearch(); }
        
        // 全データをその章から再描画
        wordList.innerHTML = '';
        const startIdx = allData.findIndex(w => w.chapter_id === id);
        currentIndex = startIdx;
        currentChapterInView = null;
        renderNextPage();
        window.scrollTo(0, 0);
    }

    loadInitialData();
</script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: index.html and word_data.json have been generated.")

if __name__ == "__main__":
    generate_index_and_data()
