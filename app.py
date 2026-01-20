import streamlit as st
import google.generativeai as genai
import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# --- 0. 環境対策 (Python 3.13 / Render対応) ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Internal Conference", page_icon="🧘", layout="centered")

# API設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # 小池さん指定の 2.5 Flash 駆動（環境に応じて調整可能）
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
keys = [
    'step', 'brain_scan', 'selected_emotion', 'social_filter_val', 
    'fatigue_val', 'hunger_val', 'digital_val', 'safebase_val', 
    'sleep_val', 'meal_input', 'activity_input',
    'sunao_input', 'social_input'
]
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else "" if 'input' in key else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

def get_context():
    now_hour = datetime.datetime.now().hour
    is_night = 21 <= now_hour or now_hour <= 6
    return "夜間（前頭前野のブレーキが弱まり、扁桃体が過敏な時間）" if is_night else "日中"

# --- STEP 2: コンディション・スキャン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 現在のステータス")
    st.markdown("身体のコンディションを教えてください")
    
    # 🔋 ハードウェア（身体・生活習慣）
    st.subheader("🔋 ハードウェア・ステータス")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["寝てない", "少しだけ", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "ボロボロ"], value="普通")
        st.session_state.meal_input = st.text_input("🥗 今日食べたもの", placeholder="例：ピザ、コンビニ、食べてない...")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそこ", "ずっと触っちゃう"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 お腹の空き具合", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")
        st.session_state.activity_input = st.text_input("🏃 今日の活動", placeholder="例：授業、仕事、何もしていない...")

    st.divider()
    
    # 心理的リソース
    st.subheader("🛡️ 心理的リソース")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.safebase_val = st.radio("🏠 今、居る場所は落ち着く？（安全基地）", 
                                              ["安心できる", "少し揺らいでいる", "孤立・戦闘態勢"], index=0)
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "爆発しそう"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務・プレッシャー）の強さ", 
                             ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "最高"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")

    # 象限判定
    e_idx, p_idx = energy_opts.index(energy) - 2, pleasant_opts.index(pleasant) - 2
    quad = "Red" if e_idx >= 0 and p_idx < 0 else "Yellow" if e_idx >= 0 and p_idx >= 0 else "Blue" if e_idx < 0 and p_idx < 0 else "Green"
    
    EM_DB = {
        "Red": ["嫌な事を考え続けてしまう", "不安", "心臓がバクバクする", "落ち着かない", "モヤモヤしている"],
        "Yellow": ["集中できている", "ワクワク", "自信がある", "挑戦したい"],
        "Blue": ["自分なんてダメだ", "布団から出られない", "消えてしまいたい", "どんより"],
        "Green": ["ほっとしている", "穏やか", "今のままでいい", "落ち着く"]
    }
    st.session_state.selected_emotion = st.selectbox(f"今の感覚に近いラベル（{quad}エリア）", ["(選択してください)"] + EM_DB[quad])

    if st.session_state.selected_emotion != "(選択してください)":
        if st.button("2.5 Flash でデバッグを開始 ➔", type="primary"): move_to(2)

elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内ログの書き出し")
    st.markdown("無理にまとめなくていい。二人の言い分を別々に吐き出して。")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🟢 本音くんの声")
        # 小池さんこだわりの注釈を追加
        st.info("💡 **ここがポイント**\n\n言いづらい、言葉にしづらいと感じることこそが、あなたの深層にある大切な『本音』である場合が多いです。スラスラ出てこなくても、断片的な言葉だけでも大丈夫。")
        st.session_state.sunao_input = st.text_area(
            "「本当はどうしたい？」", 
            placeholder="（例：まだ好きだ。思い出に浸りたい。本当はやりたくない。）", 
            height=250
        )
        
    with col_in2:
        st.markdown("### 🔴 義務さんの声")
        st.caption("※社会性フィルターを通した『〜すべき』『〜しなきゃ』という声。")
        st.session_state.social_input = st.text_area(
            "「〜しなきゃ、〜すべき」", 
            placeholder="（例：前を向かなきゃ。期待に応えなきゃ。成果を出さなきゃ。）", 
            height=250
        )

    st.divider()

    if st.button("調律プロセスを実行 ➔", type="primary"):
        with st.spinner("無意識の声を意識の部屋へエクスポート中..."):
            try:
                model = genai.GenerativeModel(model_id)
                # 小池さんの核心「言いづらさ＝本音」をプロンプトに反映
                prompt = f"""
                【解析対象】
                - ログ: 素直={st.session_state.sunao_input}, 義務={st.session_state.social_input}
                - 生活習慣: 睡眠={st.session_state.sleep_val}, 食事={st.session_state.meal_input}, 活動={st.session_state.activity_input}
                - コンディション: {get_context()}, 疲労={st.session_state.fatigue_val}, デジタル={st.session_state.digital_val}, 安全基地={st.session_state.safebase_val}

                【2.5 Flash 調律ガイド】
                1. 二つの声を「共存」させるためのカンファレンス・ログを作成してください。
                2. 特に「本音（素直）」が言葉少なであったり、抽象的であったりする場合、それが強力な「抑圧」を受けている証拠だと捉え、その背後にある切実な想いを優しく言語化してください。
                3. 無意識から意識の部屋（玄関）へ引き出す通訳の役割を果たします。
                4. 無理に仲直りさせず、不協和（不快感）そのものを「誠実さの証」として肯定してください。
                5. 生活習慣が脳に与えている影響を分析し、具体的な処方箋を3つ出してください。

                【JSON構造】
                {{
                    "sunao_claim": "本音くんの言い分（一人称）",
                    "social_claim": "義務さんの言い分（一人称）",
                    "deep_analysis": "葛藤の深層分析",
                    "lifestyle_report": "今の身体コンディションが脳に与えている影響",
                    "lifestyle_advice": ["具体的提案1", "具体的提案2", "具体的提案3"],
                    "validation": "誠実さの肯定",
                    "secure_msg": "安全基地からの言葉",
                    "sunao_pct": 0-100,
                    "social_pct": 0-100
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: 
                st.error(f"解析エラー: {e}")
                st.info("AIとの接続に失敗しました。少し時間を置いてから再度お試しください。")

    if st.button("← 戻る"): 
        move_to(1)

# --- STEP 3: カンファレンス・レポート ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 脳内カンファレンス・ログ")
    
    # ⚖️ バランスの可視化
    s_p, so_p = scan['sunao_pct'], scan['social_pct']
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.add_patch(plt.Circle((0.3, 0.5), np.sqrt(s_p)/25 + 0.1, color='#4CAF50', alpha=0.6))
    ax.add_patch(plt.Circle((0.7, 0.5), np.sqrt(so_p)/25 + 0.1, color='#FF5252', alpha=0.6))
    ax.text(0.3, 0.5, f"本音(素直)\n{s_p}%\n『本音くん』", ha='center', va='center', fontweight='bold')
    ax.text(0.7, 0.5, f"義務(社会性)\n{so_p}%\n『義務さん』", ha='center', va='center', fontweight='bold')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off'); st.pyplot(fig)
    
    # 🗣️ 二つの声の並置
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        st.success(f"**🟢 本音くん**\n\n「{scan['sunao_claim']}」")
    with col_out2:
        st.error(f"**🔴 義務さん**\n\n「{scan['social_claim']}」")
    
    st.divider()
    st.info(f"🧠 **調律師の深層解析**\n{scan['deep_analysis']}")
    
    st.subheader("🥗 ハードウェア・メンテナンス（生活習慣改善）")
    st.warning(scan['lifestyle_report'])
    for advice in scan['lifestyle_advice']:
        st.write(f"✅ {advice}")
    
    st.subheader("💎 あなたの誠実さへの証言")
    st.write(scan['validation'])
    st.markdown(f"#### 🕊️ {scan['secure_msg']}")
    
    if st.button("最初に戻る"): move_to(1)
