import json
import os
import re
from pathlib import Path
from glob import glob
from config import CHAPTER_MAP

def load_words():
    all_words = []
    json_files = ['vocabulary_data.json'] + sorted(glob('vocabulary_data_*.json'), 
                  key=lambda x: int(re.search(r'_(\d+)\.json', x).group(1)) if '_' in x else 0)
    for jf in json_files:
        if os.path.exists(jf):
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_words.extend(data.get('words', []))
            except: continue
    unique_words = {}
    for w in all_words:
        unique_words[str(w['number'])] = {"n": str(w['number']), "w": w['word'], "m": w['meaning']}
    return sorted(unique_words.values(), key=lambda x: [int(p) for p in x['n'].split('-')])

def generate_html():
    words = load_words()
    
    # チャプターをグループ化してJSに渡す
    from collections import defaultdict
    grouped = defaultdict(list)
    for s_num, title in sorted(CHAPTER_MAP.items()):
        group_name = re.search(r'【(.*?)】', title).group(1) if '【' in title else "その他"
        display_label = title.split('】')[-1] if '】' in title else title
        grouped[group_name].append({"id": s_num, "label": display_label})
    
    chapters_js = json.dumps(dict(grouped), ensure_ascii=False)
    words_js = json.dumps(words, ensure_ascii=False)
    
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>単語演習 - English Practice</title>
    <style>
        :root {{ --primary: #007bff; --success: #28a745; --bg: #f4f7f9; }}
        body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .container {{ width: 100%; max-width: 650px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: var(--primary); }}
        .setup-section, .quiz-section {{ display: none; }}
        .active {{ display: block; }}
        
        .option-group {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        label {{ display: block; font-weight: bold; margin-bottom: 8px; }}
        
        /* チャプター選択エリアの改善 */
        .chapter-container {{ max-height: 350px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #fff; }}
        .chapter-group-title {{ font-size: 0.9rem; font-weight: bold; color: #555; background: #f0f4f8; padding: 5px 10px; margin: 10px 0 5px 0; border-left: 4px solid var(--primary); }}
        .chapter-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 5px; padding-left: 5px; }}
        .chapter-item {{ font-size: 0.85rem; display: flex; align-items: center; padding: 3px 0; }}
        .chapter-item input {{ margin-right: 8px; }}
        
        .input-range {{ display: flex; align-items: center; gap: 10px; }}
        input[type="number"] {{ padding: 8px; width: 80px; }}
        
        .btn {{ background: var(--primary); color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 1rem; margin-top: 10px; }}
        .btn:hover {{ opacity: 0.9; }}
        
        .quiz-container {{ text-align: center; }}
        .card-wrapper {{ position: relative; margin: 20px 0; }}
        .card {{ border: 2px solid var(--primary); padding: 40px 20px; border-radius: 15px; cursor: pointer; min-height: 120px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; background: white; }}
        .card.flipped {{ border-color: var(--success); color: var(--success); }}
        
        .nav-controls {{ display: flex; justify-content: space-between; gap: 10px; margin-top: 15px; }}
        .nav-btn {{ flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px; cursor: pointer; background: #eee; font-weight: bold; }}
        .nav-btn:disabled {{ opacity: 0.3; cursor: not-allowed; }}

        .options-grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; margin-top: 20px; }}
        .option-btn {{ background: white; border: 2px solid #ddd; padding: 15px; border-radius: 8px; cursor: pointer; font-size: 1.1rem; }}
        .progress {{ font-size: 0.9rem; color: #666; margin-bottom: 10px; text-align: center; }}
    </style>
</head>
<body>

<div class="container">
    <h1>単語演習</h1>

    <div id="setup" class="setup-section active">
        <div class="option-group">
            <label>1. 出題範囲の指定方法</label>
            <input type="radio" name="rangeType" value="chapter" checked onclick="toggleRange()"> チャプター選択
            <input type="radio" name="rangeType" value="number" onclick="toggleRange()"> 番号指定
        </div>

        <div id="range-chapter" class="option-group">
            <label>出題チャプター (複数選択可)</label>
            <div class="chapter-container" id="chapterList"></div>
        </div>

        <div id="range-number" class="option-group" style="display:none;">
            <label>番号範囲入力</label>
            <div class="input-range">
                <input type="number" id="startNum" placeholder="開始"> 〜 
                <input type="number" id="endNum" placeholder="終了">
            </div>
        </div>

        <div class="option-group">
            <label>2. 出題順序</label>
            <input type="radio" name="orderType" value="random" checked> ランダム
            <input type="radio" name="orderType" value="sequential"> 番号順
        </div>

        <div class="option-group">
            <label>3. 演習モード</label>
            <select id="mode" style="width:100%; padding:10px; border-radius:5px;">
                <option value="card-en-ja">暗記カード (英 → 日)</option>
                <option value="card-ja-en">暗記カード (日 → 英)</option>
                <option value="quiz-en-ja">4択問題 (英 → 日)</option>
                <option value="quiz-ja-en">4択問題 (日 → 英)</option>
            </select>
        </div>

        <button class="btn" onclick="startExercise()">演習開始</button>
    </div>

    <div id="quiz" class="quiz-section">
        <div class="progress" id="progressText">0 / 0</div>
        <div class="quiz-container">
            <div id="cardArea">
                <div id="card" class="card" onclick="flipCard()">Word</div>
                <div class="nav-controls">
                    <button id="prevBtn" class="nav-btn" onclick="goBack()">← 前の単語</button>
                    <button id="nextBtn" class="nav-btn" onclick="flipCard()">次へ / 答え →</button>
                </div>
            </div>
            <div id="options" class="options-grid"></div>
        </div>
        <button class="btn" style="margin-top:30px; background:#6c757d;" onclick="location.reload()">終了して戻る</button>
    </div>
</div>

<script>
const GROUPED_CHAPTERS = {chapters_js};
const ALL_WORDS = {words_js};

// 小見出し付きチャプターリストの生成
const chapterListDiv = document.getElementById('chapterList');
for (const [group, chapters] of Object.entries(GROUPED_CHAPTERS)) {{
    const groupTitle = document.createElement('div');
    groupTitle.className = 'chapter-group-title';
    groupTitle.innerText = group;
    chapterListDiv.appendChild(groupTitle);
    
    const grid = document.createElement('div');
    grid.className = 'chapter-grid';
    
    chapters.forEach(ch => {{
        const div = document.createElement('div');
        div.className = 'chapter-item';
        div.innerHTML = `<label><input type="checkbox" name="chapters" value="${{ch.id}}"> ${{ch.label}}</label>`;
        grid.appendChild(div);
    }});
    chapterListDiv.appendChild(grid);
}}

function toggleRange() {{
    const type = document.querySelector('input[name="rangeType"]:checked').value;
    document.getElementById('range-chapter').style.display = type === 'chapter' ? 'block' : 'none';
    document.getElementById('range-number').style.display = type === 'number' ? 'block' : 'none';
}}

let quizWords = [];
let currentIndex = 0;
let isFlipped = false;

function startExercise() {{
    const type = document.querySelector('input[name="rangeType"]:checked').value;
    const order = document.querySelector('input[name="orderType"]:checked').value;
    
    if(type === 'chapter') {{
        const selected = Array.from(document.querySelectorAll('input[name="chapters"]:checked')).map(cb => parseInt(cb.value));
        if(selected.length === 0) {{ alert("チャプターを選択してください"); return; }}
        
        // フラットな閾値リストを作成
        let thresholds = [];
        for(const chapters of Object.values(GROUPED_CHAPTERS)) {{
            chapters.forEach(ch => thresholds.push(parseInt(ch.id)));
        }}
        thresholds.sort((a,b)=>a-b);

        quizWords = ALL_WORDS.filter(w => {{
            const n = parseInt(w.n.split('-')[0]);
            const chapterId = thresholds.slice().reverse().find(t => n >= t);
            return selected.includes(chapterId);
        }});
    }} else {{
        const start = parseInt(document.getElementById('startNum').value);
        const end = parseInt(document.getElementById('endNum').value);
        if(isNaN(start) || isNaN(end)) {{ alert("番号を入力してください"); return; }}
        quizWords = ALL_WORDS.filter(w => {{
            const n = parseInt(w.n.split('-')[0]);
            return n >= start && n <= end;
        }});
    }}

    if(quizWords.length === 0) {{ alert("条件に合う単語がありませんでした。"); return; }}
    
    if(order === 'random') {{
        quizWords.sort(() => Math.random() - 0.5);
    }} else {{
        quizWords.sort((a, b) => {{
            const pa = a.n.split('-').map(Number);
            const pb = b.n.split('-').map(Number);
            return pa[0] !== pb[0] ? pa[0] - pb[0] : (pa[1] || 0) - (pb[1] || 0);
        }});
    }}
    
    currentIndex = 0;
    document.getElementById('setup').classList.remove('active');
    document.getElementById('quiz').classList.add('active');
    showQuestion();
}}

function showQuestion() {{
    isFlipped = false;
    const word = quizWords[currentIndex];
    const mode = document.getElementById('mode').value;
    document.getElementById('progressText').innerText = `STEP: ${{currentIndex + 1}} / ${{quizWords.length}} (No. ${{word.n}})`;
    
    const card = document.getElementById('card');
    const optionsDiv = document.getElementById('options');
    const cardArea = document.getElementById('cardArea');
    const prevBtn = document.getElementById('prevBtn');

    if(mode.startsWith('card')) {{
        cardArea.style.display = 'block';
        optionsDiv.style.display = 'none';
        card.classList.remove('flipped');
        card.innerText = mode === 'card-en-ja' ? word.w : word.m;
        prevBtn.disabled = currentIndex === 0;
    }} else {{
        cardArea.style.display = 'none';
        optionsDiv.style.display = 'grid';
        const isEnJa = mode === 'quiz-en-ja';
        
        optionsDiv.innerHTML = `<div class="card" style="cursor:default; font-size:1.5rem; margin-bottom:10px;">${{isEnJa ? word.w : word.m}}</div>`;
        
        let choices = [word];
        while(choices.length < 4 && ALL_WORDS.length > 4) {{
            const r = ALL_WORDS[Math.floor(Math.random() * ALL_WORDS.length)];
            if(!choices.find(o => o.n === r.n)) choices.push(r);
        }}
        choices.sort(() => Math.random() - 0.5);
        
        choices.forEach(opt => {{
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = isEnJa ? opt.m : opt.w;
            btn.onclick = () => {{
                if(opt.n === word.n) {{
                    btn.style.background = '#d4edda';
                    setTimeout(() => {{ currentIndex++; checkEnd(); }}, 400);
                }} else {{
                    btn.style.background = '#f8d7da';
                    btn.disabled = true;
                }}
            }};
            optionsDiv.appendChild(btn);
        }});
    }}
}}

function flipCard() {{
    const mode = document.getElementById('mode').value;
    const word = quizWords[currentIndex];
    const card = document.getElementById('card');
    if(!isFlipped) {{
        card.innerText = mode === 'card-en-ja' ? word.m : word.w;
        card.classList.add('flipped');
        isFlipped = true;
    }} else {{
        currentIndex++;
        checkEnd();
    }}
}}

function goBack() {{
    if(currentIndex > 0) {{
        currentIndex--;
        showQuestion();
    }}
}}

function checkEnd() {{
    if(currentIndex < quizWords.length) showQuestion();
    else {{ alert("全問終了しました！"); location.reload(); }}
}}
</script>
</body>
</html>"""

    with open("exercise.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✓ exercise.html has been generated with grouped chapter layout.")

if __name__ == "__main__":
    generate_html()
