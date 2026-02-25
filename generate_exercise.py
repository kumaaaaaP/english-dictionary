import json
import os
import re
from pathlib import Path
from glob import glob
from config import CHAPTER_MAP

def get_json_file_list():
    json_files = ['vocabulary_data.json'] + sorted(glob('vocabulary_data_*.json'), 
                  key=lambda x: int(re.search(r'_(\d+)\.json', x).group(1)) if '_' in x else 0)
    return [jf for jf in json_files if os.path.exists(jf)]

def generate_html():
    from collections import defaultdict
    grouped = defaultdict(list)
    for s_num, title in sorted(CHAPTER_MAP.items()):
        group_name = re.search(r'【(.*?)】', title).group(1) if '【' in title else "その他"
        display_label = title.split('】')[-1] if '】' in title else title
        grouped[group_name].append({"id": s_num, "label": display_label})
    
    chapters_js = json.dumps(dict(grouped), ensure_ascii=False)
    json_files_js = json.dumps(get_json_file_list())
    
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>単語演習 - English Practice</title>
    <style>
        :root {{ --primary: #007bff; --success: #28a745; --danger: #dc3545; --bg: #f4f7f9; }}
        body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .container {{ width: 100%; max-width: 650px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: var(--primary); }}
        .setup-section, .quiz-section {{ display: none; }}
        .active {{ display: block; }}
        
        .chapter-container {{ max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-bottom: 10px; }}
        .chapter-group-title {{ font-size: 0.9rem; font-weight: bold; color: #555; background: #f0f4f8; padding: 5px 10px; margin: 10px 0 5px 0; border-left: 4px solid var(--primary); }}
        .chapter-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 5px; }}
        
        .option-group {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        label {{ display: block; font-weight: bold; margin-bottom: 8px; }}
        .btn {{ background: var(--primary); color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 1rem; margin-top: 10px; }}
        .btn:disabled {{ background: #ccc; }}

        /* 穴埋めモード用スタイル */
        .fill-blank-area {{ text-align: left; background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #dee2e6; }}
        .sentence-ja {{ font-size: 0.95rem; color: #666; margin-bottom: 15px; line-height: 1.5; }}
        .sentence-en {{ font-size: 1.2rem; font-weight: 500; line-height: 1.8; }}
        .blank-input {{ border: none; border-bottom: 2px solid var(--primary); outline: none; background: transparent; font-size: 1.2rem; text-align: center; color: var(--primary); width: 150px; padding: 0 5px; }}
        .blank-input.correct {{ color: var(--success); border-color: var(--success); }}
        .blank-input.wrong {{ color: var(--danger); border-color: var(--danger); }}
        .feedback {{ margin-top: 10px; font-weight: bold; min-height: 1.5em; }}
        
        .card {{ border: 2px solid var(--primary); padding: 40px 20px; border-radius: 15px; text-align: center; min-height: 120px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; background: white; }}
        .progress {{ font-size: 0.9rem; color: #666; margin-bottom: 10px; text-align: center; }}
    </style>
</head>
<body>

<div class="container">
    <h1>単語演習</h1>
    <div id="loadingStatus" style="text-align:center;">データを読み込んでいます...</div>

    <div id="setup" class="setup-section">
        <div class="option-group">
            <label>1. 出題範囲の指定</label>
            <div class="chapter-container" id="chapterList"></div>
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
                <option value="fill-blank">例文穴埋め (スペリング入力)</option>
            </select>
        </div>
        <button id="startBtn" class="btn" onclick="startExercise()" disabled>準備中...</button>
    </div>

    <div id="quiz" class="quiz-section">
        <div class="progress" id="progressText">0 / 0</div>
        <div id="quizContainer"></div>
        <button id="mainActionBtn" class="btn" style="display:none;"></button>
        <button class="btn" style="margin-top:20px; background:#6c757d;" onclick="location.reload()">終了して戻る</button>
    </div>
</div>

<script>
const GROUPED_CHAPTERS = {chapters_js};
const JSON_FILES = {json_files_js};
let ALL_WORDS = [];

async function loadAllData() {{
    try {{
        const results = await Promise.all(JSON_FILES.map(file => fetch(file).then(r => r.json())));
        results.forEach(data => {{
            if (data.words) {{
                data.words.forEach(w => {{
                    // 例文データを保持するように拡張
                    ALL_WORDS.push({{ 
                        n: String(w.number), 
                        w: w.word, 
                        m: w.meaning,
                        examples: w.example_sections || []
                    }});
                }});
            }}
        }});
        document.getElementById('loadingStatus').style.display = 'none';
        document.getElementById('setup').classList.add('active');
        document.getElementById('startBtn').disabled = false;
        document.getElementById('startBtn').innerText = '演習開始';
    }} catch (e) {{ console.error(e); }}
}}

// チャプターリスト生成
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

let quizWords = [];
let currentIndex = 0;
let isFlipped = false;

function startExercise() {{
    const selected = Array.from(document.querySelectorAll('input[name="chapters"]:checked')).map(cb => parseInt(cb.value));
    if(selected.length === 0) {{ alert("チャプターを選択してください"); return; }}
    
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

    const mode = document.getElementById('mode').value;
    if(mode === 'fill-blank') {{
        quizWords = quizWords.filter(w => w.examples.length > 0);
        if(quizWords.length === 0) {{ alert("例文データがある単語がありませんでした。"); return; }}
    }}

    if(document.querySelector('input[name="orderType"]:checked').value === 'random') {{
        quizWords.sort(() => Math.random() - 0.5);
    }}

    currentIndex = 0;
    document.getElementById('setup').classList.remove('active');
    document.getElementById('quiz').classList.add('active');
    showQuestion();
}}

function showQuestion() {{
    const word = quizWords[currentIndex];
    const mode = document.getElementById('mode').value;
    const container = document.getElementById('quizContainer');
    const mainBtn = document.getElementById('mainActionBtn');
    
    document.getElementById('progressText').innerText = `STEP: ${{currentIndex + 1}} / ${{quizWords.length}} (No. ${{word.n}})`;
    container.innerHTML = '';
    mainBtn.style.display = 'none';

    if(mode === 'fill-blank') {{
        showFillBlank(word);
    }} else if(mode.startsWith('card')) {{
        showCard(word, mode);
    }} else {{
        showQuiz(word, mode);
    }}
}}

// --- 例文穴埋めモード ---
function showFillBlank(word) {{
    const container = document.getElementById('quizContainer');
    // ランダムに一つの例文セクションから一つの例文を選択
    const section = word.examples[Math.floor(Math.random() * word.examples.length)];
    const ex = section.examples[Math.floor(Math.random() * section.examples.length)];
    
    const target = ex.highlight;
    const parts = ex.en.split(new RegExp(`(${{target}})`, 'i'));

    container.innerHTML = `
        <div class="fill-blank-area">
            <div class="sentence-ja">和訳: ${{ex.ja}}</div>
            <div class="sentence-en" id="sentenceEn"></div>
            <div class="feedback" id="feedback"></div>
        </div>
    `;

    const sentenceEn = document.getElementById('sentenceEn');
    parts.forEach(p => {{
        if(p.toLowerCase() === target.toLowerCase()) {{
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'blank-input';
            input.id = 'answerInput';
            input.autocomplete = 'off';
            input.onkeypress = (e) => {{ if(e.key === 'Enter') checkFillBlank(target); }};
            sentenceEn.appendChild(input);
            setTimeout(() => input.focus(), 100);
        }} else {{
            sentenceEn.appendChild(document.createTextNode(p));
        }}
    }});

    const mainBtn = document.getElementById('mainActionBtn');
    mainBtn.innerText = '判定する';
    mainBtn.style.display = 'block';
    mainBtn.onclick = () => checkFillBlank(target);
}}

function checkFillBlank(correctAnswer) {{
    const input = document.getElementById('answerInput');
    const feedback = document.getElementById('feedback');
    const mainBtn = document.getElementById('mainActionBtn');
    const userAns = input.value.trim().toLowerCase();
    
    if(userAns === correctAnswer.toLowerCase()) {{
        input.className = 'blank-input correct';
        feedback.innerText = '✨ 正解！';
        feedback.style.color = 'var(--success)';
        mainBtn.innerText = '次の問題へ';
        mainBtn.onclick = () => {{ currentIndex++; checkEnd(); }};
    }} else {{
        input.className = 'blank-input wrong';
        feedback.innerText = `❌ 惜しい！ 正解は: ${{correctAnswer}}`;
        feedback.style.color = 'var(--danger)';
        mainBtn.innerText = '確認して次へ';
        mainBtn.onclick = () => {{ currentIndex++; checkEnd(); }};
    }}
}}

// --- 暗記カードモード ---
function showCard(word, mode) {{
    const container = document.getElementById('quizContainer');
    isFlipped = false;
    container.innerHTML = `
        <div id="card" class="card" onclick="flipCard()">
            ${{mode === 'card-en-ja' ? word.w : word.m}}
        </div>
        <div class="nav-controls">
            <button id="prevBtn" class="nav-btn" onclick="goBack()" ${{currentIndex === 0 ? 'disabled' : ''}}>← 前の単語</button>
            <button id="nextBtn" class="nav-btn" onclick="flipCard()">次へ / 答え →</button>
        </div>
    `;
}}

function flipCard() {{
    const word = quizWords[currentIndex];
    const mode = document.getElementById('mode').value;
    const card = document.getElementById('card');
    if(!isFlipped) {{
        card.innerText = mode === 'card-en-ja' ? word.m : word.w;
        card.classList.add('flipped');
        isFlipped = true;
    }} else {{
        currentIndex++; checkEnd();
    }}
}}

// --- 4択クイズモード ---
function showQuiz(word, mode) {{
    const container = document.getElementById('quizContainer');
    const isEnJa = mode === 'quiz-en-ja';
    container.innerHTML = `<div class="card" style="cursor:default; font-size:1.5rem; margin-bottom:10px;">${{isEnJa ? word.w : word.m}}</div><div class="options-grid" id="options"></div>`;
    
    let choices = [word];
    while(choices.length < 4 && ALL_WORDS.length > 4) {{
        const r = ALL_WORDS[Math.floor(Math.random() * ALL_WORDS.length)];
        if(!choices.find(o => o.n === r.n)) choices.push(r);
    }}
    choices.sort(() => Math.random() - 0.5);
    
    const optionsDiv = document.getElementById('options');
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

function goBack() {{ if(currentIndex > 0) {{ currentIndex--; showQuestion(); }} }}
function checkEnd() {{ if(currentIndex < quizWords.length) showQuestion(); else {{ alert("全問終了しました！"); location.reload(); }} }}

loadAllData();
</script>
</body>
</html>"""

    with open("exercise.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✓ exercise.html updated with Fill-in-the-blank mode.")

if __name__ == "__main__":
    generate_html()
