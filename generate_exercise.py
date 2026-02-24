import json
import os
import re
from pathlib import Path
from glob import glob

# build_index.py から CHAPTER_MAP を引用（一貫性のため）
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
    3974: "【東進上級英単語1000】ステージ1",
    4074: "【東進上級英単語1000】ステージ2",
    4174: "【東進上級英単語1000】ステージ3",
    4274: "【東進上級英単語1000】ステージ4",
    4374: "【東進上級英単語1000】ステージ5",
    4474: "【東進上級英単語1000】ステージ6",
    4574: "【東進上級英単語1000】ステージ7",
    4674: "【東進上級英単語1000】ステージ8",
    4774: "【東進上級英単語1000】ステージ9",
    4874: "【東進上級英単語1000】ステージ10",
    10001: "【LEAP】1〜100",
    10101: "【LEAP】101〜200",
    10201: "【LEAP】201〜300",
    10301: "【LEAP】301〜400",
    10401: "【LEAP】401〜500",
    10501: "【LEAP】501〜600",
    10601: "【LEAP】601〜700",
    10701: "【LEAP】701〜800",
    10801: "【LEAP】801〜900",
    10901: "【LEAP】901〜1000",
    11001: "【LEAP】1001〜1100",
    11101: "【LEAP】1101〜1200",
    11201: "【LEAP】1201〜1300",
    11301: "【LEAP】1301〜1400",
    11401: "【LEAP】1401〜1500",
    11501: "【LEAP】1501〜1600",
    11601: "【LEAP】1601〜1700",
    11701: "【LEAP】1701〜1800",
    11801: "【LEAP】1801〜1900",
    11901: "【LEAP】1901〜1935"
}

def load_words():
    all_words = []
    json_files = ['vocabulary_data.json'] + sorted(glob('vocabulary_data_*.json'), 
                  key=lambda x: int(re.search(r'_(\d+)\.json', x).group(1)) if '_' in x else 0)
    
    for jf in json_files:
        if os.path.exists(jf):
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_words.extend(data.get('words', []))
    
    # 重複削除とソート (422-2などのサブ番号対応)
    unique_words = {}
    for w in all_words:
        unique_words[str(w['number'])] = {"n": str(w['number']), "w": w['word'], "m": w['meaning']}
    
    return sorted(unique_words.values(), key=lambda x: [int(p) for p in x['n'].split('-')])

def generate_html():
    words = load_words()
    # チャプター情報のJS化
    chapters_js = json.dumps(CHAPTER_MAP, ensure_ascii=False)
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
        .container {{ width: 100%; max-width: 600px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: var(--primary); }}
        .setup-section {{ display: block; }}
        .quiz-section {{ display: none; text-align: center; }}
        
        .option-group {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        label {{ display: block; font-weight: bold; margin-bottom: 8px; }}
        
        /* チャプター選択用グリッド */
        .chapter-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
        .chapter-item {{ font-size: 0.8rem; display: flex; align-items: center; }}
        
        .input-range {{ display: flex; align-items: center; gap: 10px; }}
        input[type="number"] {{ padding: 8px; width: 80px; }}
        .error-msg {{ color: red; font-size: 0.85rem; margin-top: 5px; display: none; }}
        
        .btn {{ background: var(--primary); color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 1rem; margin-top: 10px; }}
        .btn-success {{ background: var(--success); }}

        /* クイズ画面 */
        .card {{ border: 2px solid var(--primary); padding: 40px 20px; border-radius: 15px; margin: 20px 0; cursor: pointer; min-height: 100px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; transition: transform 0.2s; }}
        .card:active {{ transform: scale(0.98); }}
        .options-grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; }}
        .option-btn {{ background: white; border: 2px solid #ddd; padding: 15px; border-radius: 8px; cursor: pointer; font-size: 1.1rem; }}
        .option-btn:hover {{ border-color: var(--primary); background: #f0f7ff; }}
        .progress {{ font-size: 0.9rem; color: #666; margin-bottom: 10px; }}
    </style>
</head>
<body>

<div class="container">
    <h1>単語演習</h1>

    <div id="setup" class="setup-section">
        <div class="option-group">
            <label>1. 出題方法の選択</label>
            <input type="radio" name="rangeType" value="chapter" checked onclick="toggleRange()"> チャプター選択
            <input type="radio" name="rangeType" value="number" onclick="toggleRange()"> 番号指定
        </div>

        <div id="range-chapter" class="option-group">
            <label>出題チャプター (複数選択可)</label>
            <div class="chapter-grid" id="chapterList"></div>
        </div>

        <div id="range-number" class="option-group" style="display:none;">
            <label>番号範囲入力</label>
            <div class="input-range">
                <input type="number" id="startNum" placeholder="開始"> 〜 
                <input type="number" id="endNum" placeholder="終了">
            </div>
            <div id="numError" class="error-msg"></div>
        </div>

        <div class="option-group">
            <label>2. 演習モード</label>
            <select id="mode" style="width:100%; padding:10px;">
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
        <div id="questionArea">
            <div id="card" class="card" onclick="flipCard()">Word</div>
            <div id="options" class="options-grid"></div>
        </div>
        <button class="btn" style="margin-top:30px; background:#6c757d;" onclick="location.reload()">終了して戻る</button>
    </div>
</div>

<script>
const CHAPTER_MAP = {chapters_js};
const ALL_WORDS = {words_js};

// 初期化: チャプター一覧の生成
const chapterListDiv = document.getElementById('chapterList');
Object.keys(CHAPTER_MAP).sort((a,b)=>a-b).forEach(id => {{
    const div = document.createElement('div');
    div.className = 'chapter-item';
    div.innerHTML = `<input type="checkbox" name="chapters" value="${{id}}"> ${{CHAPTER_MAP[id]}}`;
    chapterListDiv.appendChild(div);
}});

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
    const mode = document.getElementById('mode').value;
    
    if(type === 'chapter') {{
        const selected = Array.from(document.querySelectorAll('input[name="chapters"]:checked')).map(cb => parseInt(cb.value));
        if(selected.length === 0) {{ alert("チャプターを選択してください"); return; }}
        
        // チャプターの境界線を考慮してフィルタリング
        const sortedThresholds = Object.keys(CHAPTER_MAP).map(Number).sort((a,b)=>a-b);
        quizWords = ALL_WORDS.filter(w => {{
            const n = parseInt(w.n.split('-')[0]);
            const chapterId = sortedThresholds.slice().reverse().find(t => n >= t);
            return selected.includes(chapterId);
        }});
    }} else {{
        const start = parseInt(document.getElementById('startNum').value);
        const end = parseInt(document.getElementById('endNum').value);
        const maxNum = Math.max(...ALL_WORDS.map(w => parseInt(w.n.split('-')[0])));
        
        if(isNaN(start) || isNaN(end) || start < 1 || end > maxNum || start > end) {{
            const msg = `1〜${{maxNum}}の範囲で正しく入力してください`;
            document.getElementById('numError').innerText = msg;
            document.getElementById('numError').style.display = 'block';
            return;
        }}
        quizWords = ALL_WORDS.filter(w => {{
            const n = parseInt(w.n.split('-')[0]);
            return n >= start && n <= end;
        }});
    }}

    if(quizWords.length === 0) {{ alert("範囲内に単語が見つかりませんでした。"); return; }}
    
    // シャッフル
    quizWords.sort(() => Math.random() - 0.5);
    
    document.getElementById('setup').style.display = 'none';
    document.getElementById('quiz').style.display = 'block';
    showQuestion();
}}

function showQuestion() {{
    isFlipped = false;
    const word = quizWords[currentIndex];
    const mode = document.getElementById('mode').value;
    document.getElementById('progressText').innerText = `${{currentIndex + 1}} / ${{quizWords.length}}`;
    
    const card = document.getElementById('card');
    const optionsDiv = document.getElementById('options');
    
    if(mode.startsWith('card')) {{
        card.style.display = 'flex';
        optionsDiv.style.display = 'none';
        card.innerText = mode === 'card-en-ja' ? word.w : word.m;
    }} else {{
        card.style.display = 'flex';
        card.style.fontSize = '1.5rem';
        card.style.cursor = 'default';
        optionsDiv.style.display = 'grid';
        
        const isEnJa = mode === 'quiz-en-ja';
        card.innerText = isEnJa ? word.w : word.m;
        
        // 選択肢作成
        let options = [word];
        while(options.length < 4 && ALL_WORDS.length > 4) {{
            const randomWord = ALL_WORDS[Math.floor(Math.random() * ALL_WORDS.length)];
            if(!options.find(o => o.n === randomWord.n)) options.push(randomWord);
        }}
        options.sort(() => Math.random() - 0.5);
        
        optionsDiv.innerHTML = '';
        options.forEach(opt => {{
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = isEnJa ? opt.m : opt.w;
            btn.onclick = () => checkAnswer(opt.n === word.n, btn);
            optionsDiv.appendChild(btn);
        }});
    }}
}}

function flipCard() {{
    const mode = document.getElementById('mode').value;
    if(!mode.startsWith('card')) return;
    
    const word = quizWords[currentIndex];
    const card = document.getElementById('card');
    
    if(!isFlipped) {{
        card.innerText = mode === 'card-en-ja' ? word.m : word.w;
        card.style.color = 'var(--success)';
        isFlipped = true;
    }} else {{
        currentIndex++;
        if(currentIndex < quizWords.length) {{
            card.style.color = 'black';
            showQuestion();
        }} else {{
            alert("全問終了しました！");
            location.reload();
        }}
    }}
}}

function checkAnswer(isCorrect, btn) {{
    if(isCorrect) {{
        btn.style.background = '#d4edda';
        btn.style.borderColor = 'var(--success)';
        setTimeout(() => {{
            currentIndex++;
            if(currentIndex < quizWords.length) showQuestion();
            else {{ alert("全問終了しました！"); location.reload(); }}
        }}, 500);
    }} else {{
        btn.style.background = '#f8d7da';
        btn.style.borderColor = '#dc3545';
        btn.disabled = true;
    }}
}}
</script>
</body>
</html>"""

    with open("exercise.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✓ exercise.html has been generated.")

if __name__ == "__main__":
    generate_html()
