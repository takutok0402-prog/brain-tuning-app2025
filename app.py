import streamlit as st
import google.generativeai as genai
import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# --- 0. 文字化け・環境対策 (Python 3.13 / Render対応) ---
# japanize-matplotlibを使わず、標準的なフォント優先順位を設定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Attachment Tuning", page_icon="🧘", layout="centered")

# API設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
for key in ['step', 'brain_scan', 'selected_emotion', 'social_filter_val', 
            'fatigue_val', 'hunger_val', 'digital_val', 'safebase_val', 
            'sunao_input', 'social_input']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else "" if 'input' in key else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

def get_context():
    now_hour = datetime.datetime.now().hour
    is_night = 21 <= now_hour or now_hour <= 6
    return "夜間（前頭前野の機能が低下し、扁桃体が過敏な時間）" if is_night else "日中"

# --- STEP 1: コンディション・チェックイン（機能追加版） ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 現在のステータス")
    st.markdown("今のあなたの『身体の状態』を多角的にスキャンします。")
    
    # 🔋 身体・環境リソース
    st.subheader("🔋 ハードウェア・ステータス")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.fatigue_val = st.select_slider("😫 疲労度・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "限界"], value="普通")
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそ手に取る", "ずっと触っちゃう"], value="少なめ")
    with v_col2:
        st.session_state.hunger_val = st.select_slider("🍕 エネルギー（空腹）", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")
        st.session_state.safebase_val = st.radio("🏠 今、居る場所が安全だとを感じられますか？落ち着きますか？", 
                                              ["感じられる（安全）", "少し揺らいでいる", "感じられない（孤立・戦闘態勢）"], index=0)
    
    st.divider()
    
    # 🧠 脳内座標
    st.markdown("##### 🧠 脳内座標の確認")
    col1, col2 = st.columns(2)
    with col1:
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "抑えられない"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with col2:
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "心地よい"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")
    
    # 象限判定
    e_idx = energy_opts.index(energy) - 2
    p_idx = pleasant_opts.index(pleasant) - 2
    quadrant = "Red" if e_idx >= 0 and p_idx < 0 else "Yellow" if e_idx >= 0 and p_idx >= 0 else "Blue" if e_idx < 0 and p_idx < 0 else "Green"
    
    EMOTION_DB = {
        "Red": ["嫌な事を考え続けてしまう", "不安", "心臓がバクバクする", "焦り", "落ち着かない", "モヤモしている"],
        "Yellow": ["集中できている", "ワクワク", "自信がある", "挑戦したい"],
        "Blue": ["自分なんてダメだ", "布団から出られない", "消えてしまいたい", "無気力", "どんより"],
        "Green": ["ほっとしている", "穏やか", "今のままでいい", "落ち着く"]
    }
    st.session_state.selected_emotion = st.selectbox(f"今の感覚に近いラベル（{quadrant}エリア）", ["(選択してください)"] + EMOTION_DB[quadrant])

    st.divider()
    st.markdown("##### 社会性フィルターの密度")
    st.session_state.social_filter_val = st.radio("周囲の期待や意見、『〜すべき』という常識をどのくらい重く感じていますか？", 
                             ["全く気にならない", "少し気になる", "すごく気になる"], index=1)

    if st.session_state.selected_emotion != "(選択してください)":
        if st.button("2.5 Flash で深層デバッグを開始 ➔", type="primary"):
            move_to(2)

# --- STEP 2: 思考ログの書き出し ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 予測ログの全出力")
    st.markdown(f"**「{st.session_state.selected_emotion}」**を分離します。")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 本音（素直）")
        st.session_state.sunao_input = st.text_area("「本当はどうしたい？」", placeholder="例：もう休みたい、一人の時間が欲しい...", height=200, key="sunao_area")
    with col2:
        st.markdown("### 🔴 義務（社会性）")
        st.session_state.social_input = st.text_area("「〜しなきゃ、〜すべき」", placeholder="例：成果を出さなきゃ、いい人でいなきゃ...", height=200, key="social_area")
    
    if st.button("2.5 Flash 調律プロセスを実行 ➔", type="primary"):
        with st.spinner("多角的な要因からバグを解析中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                【解析対象】
                - 本音: {st.session_state.sunao_input}
                - 義務: {st.session_state.social_input}
                - コンディション: {get_context()}, 疲労={st.session_state.fatigue_val}, 空腹={st.session_state.hunger_val}, デジタル・ノイズ={st.session_state.digital_val}, 安全基地={st.session_state.safebase_val}

                【2.5 Flash 調律ガイドライン】
                1. 「素直」と「社会性」の脳内シェア（100%）を推定してください。
                2. 特に『デジタル・ノイズ』と『安全基地の不在』が、どのように脳をサバイバルモード（扁桃体優位）にし、義務感を膨張させているか分析してください。
                3. このしんどさは「脳の生存戦略」であることを強調し、ユーザーを深く肯定してください。

                【JSON構造】
                {{
                    "sunao_pct": 0-100,
                    "social_pct": 0-100,
                    "sunao_tag": "本音の短縮タグ",
                    "social_tag": "義務の短縮タグ",
                    "analysis": "多角的な要因を含む深層分析",
                    "hardware_report": "疲労・空腹・デジタルノイズの影響",
                    "attachment_report": "安全基地の状態がもたらす心理的影響",
                    "validation": "誠実さの肯定",
                    "next_step": "今すぐできるリセットアクション",
                    "secure_msg": "安全基地からの言葉"
                }}
                """
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(response.text)
                move_to(3)
            except Exception as e:
                st.error(f"解析エラー: {e}")

    if st.button("← 戻る"): move_to(1) 

# --- STEP 3: 調律結果の可視化 ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了レポート")
    
    # ⚖️ バランスの可視化
    s_pct, so_pct = scan['sunao_pct'], scan['social_pct']
    fig, ax = plt.subplots(figsize=(8, 4))
    c_sunao = plt.Circle((0.3, 0.5), np.sqrt(s_pct)/25 + 0.1, color='#4CAF50', alpha=0.6)
    c_social = plt.Circle((0.7, 0.5), np.sqrt(so_pct)/25 + 0.1, color='#FF5252', alpha=0.6)
    ax.add_patch(c_sunao); ax.add_patch(c_social)
    ax.text(0.3, 0.5, f"本音(素直)\n{s_pct}%\n『{scan['sunao_tag']}』", ha='center', va='center', fontweight='bold')
    ax.text(0.7, 0.5, f"義務(社会性)\n{so_pct}%\n『{scan['social_tag']}』", ha='center', va='center', fontweight='bold')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    st.pyplot(fig)
    
    st.info(scan['analysis'])
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.warning(f"🔋 **システム負荷レポート**\n{scan['hardware_report']}")
    with col_b:
        st.error(f"🛡️ **アタッチメント解析**\n{scan['attachment_report']}")
    
    st.subheader("💎 あなたの誠実さへの証言")
    st.write(scan['validation'])
    
    st.success(f"**💡 推奨されるリセット:** {scan['next_step']}")
    st.markdown(f"#### 🕊️ {scan['secure_msg']}")
    
    if st.button("最初に戻る"): move_to(1)
