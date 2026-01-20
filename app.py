import streamlit as st
import google.generativeai as genai
import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Attachment Tuning", page_icon="🧘", layout="centered")

# API設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # 高速・高機能な 2.5 Flash を指定
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。環境変数またはStreamlit Secretsを確認してください。")

# セッション状態の初期化
for key in ['step', 'brain_scan', 'selected_emotion', 'social_filter_val', 'fatigue_val', 'hunger_val', 'sunao_input', 'social_input']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else "" if 'input' in key else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

def get_context():
    now_hour = datetime.datetime.now().hour
    is_night = 21 <= now_hour or now_hour <= 6
    return "夜間（前頭前野のブレーキが弱まり、扁桃体の反応が鋭敏になる時間）" if is_night else "日中"

# --- STEP 1: ハードウェア & 感情チェック ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 現在のステータス")
    st.markdown("今のマシンのコンディションを教えてください。")
    
    st.subheader("🔋 バイタル・リソース")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.fatigue_val = st.select_slider("😫 疲労度・眠気", options=["絶好調", "普通", "少し消耗", "限界"], value="普通")
    with v_col2:
        st.session_state.hunger_val = st.select_slider("🍕 エネルギー（空腹）", options=["満腹", "普通", "低下", "ガス欠"], value="普通")
    
    st.divider()
    st.markdown("##### 🧠 脳内座標の確認")
    col1, col2 = st.columns(2)
    with col1:
        energy_opts = ["動けない", "低め", "普通", "高め", "過剰"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with col2:
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "心地よい"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")
    
    # 象限の判定
    e_idx = energy_opts.index(energy) - 2
    p_idx = pleasant_opts.index(pleasant) - 2
    quadrant = "Red" if e_idx >= 0 and p_idx < 0 else "Yellow" if e_idx >= 0 and p_idx >= 0 else "Blue" if e_idx < 0 and p_idx < 0 else "Green"
    
    EMOTION_DB = {
        "Red": ["答え合わせが止まらない", "嫌われたくない", "心臓がバクバクする", "パニック", "焦燥感"],
        "Yellow": ["集中できている", "ワクワク", "自信がある", "いきいき", "挑戦したい"],
        "Blue": ["自分なんてダメだ", "布団から出られない", "消えてしまいたい", "無気力", "感情の麻痺"],
        "Green": ["ほっとしている", "穏やか", "今のままでいい", "安心", "深い呼吸"]
    }
    st.session_state.selected_emotion = st.selectbox(f"今の感覚に近いラベル（{quadrant}エリア）", ["(選択してください)"] + EMOTION_DB[quadrant])

    st.divider()
    st.markdown("##### 社会性フィルターの密度")
    st.session_state.social_filter_val = st.radio("誰かの視線や『〜すべき』という期待をどのくらい感じていますか？", 
                             ["何も気にならない", "少し気になる", "すごく気になる"], index=1)

    if st.session_state.selected_emotion != "(選択してください)":
        if st.button("2.5 Flash で解析を開始 ➔", type="primary"):
            move_to(2)

# --- STEP 2: 思考ログの書き出し ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内ログの書き出し")
    st.markdown(f"**「{st.session_state.selected_emotion}」**を『素直』と『社会性』に分離します。")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 本音（素直）")
        st.session_state.sunao_input = st.text_area(
            "「本当はこうしたい、こう思ってる」",
            placeholder="例：疲れたからもう帰りたい、星空だけ見ていたい...",
            height=200, key="sunao_area"
        )
    with col2:
        st.markdown("### 🔴 義務（社会性）")
        st.session_state.social_input = st.text_area(
            "「〜しなきゃ、〜した方がいい」",
            placeholder="例：元を取らないともったいない、失礼のないようにしなきゃ...",
            height=200, key="social_area"
        )
    
    if st.button("調律プロセスを実行 ➔", type="primary"):
        with st.spinner("思考の境界線をスキャンしています..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                【解析対象】
                - 本音: {st.session_state.sunao_input}
                - 義務: {st.session_state.social_input}
                - 条件: {get_context()}, 疲労={st.session_state.fatigue_val}, 空腹={st.session_state.hunger_val}

                【ガイドライン】
                1. 「素直」と「社会性」の脳内シェア（合計100%）を推定してください。
                2. 疲労や時間帯が「義務感」を過剰に重く見せている可能性を解説してください。
                3. 決めつけを排し、ユーザーの葛藤を誠実さの証として肯定してください。

                【JSON構造】
                {{
                    "sunao_pct": 0-100,
                    "social_pct": 0-100,
                    "sunao_tag": "本音の短縮タグ",
                    "social_tag": "義務の短縮タグ",
                    "deep_analysis": "葛藤の分析",
                    "hardware_effect": "身体要因の影響",
                    "validation": "誠実さの肯定",
                    "next_step": "今すぐできるアクション",
                    "secure_base_msg": "安全基地からの言葉"
                }}
                """
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(response.text)
                move_to(3)
            except Exception as e:
                st.error(f"調律エラー: {e}")

    if st.button("← 戻る"): move_to(1) 

# --- STEP 3: 調律結果の可視化 ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了レポート")
    
    # ⚖️ バランスの可視化
    s_pct = scan['sunao_pct']
    so_pct = scan['social_pct']
    
    fig, ax = plt.subplots(figsize=(8, 4))
    c_sunao = plt.Circle((0.3, 0.5), np.sqrt(s_pct)/25 + 0.1, color='#4CAF50', alpha=0.6)
    c_social = plt.Circle((0.7, 0.5), np.sqrt(so_pct)/25 + 0.1, color='#FF5252', alpha=0.6)
    ax.add_patch(c_sunao)
    ax.add_patch(c_social)
    
    ax.text(0.3, 0.5, f"本音(素直)\n{s_pct}%\n『{scan['sunao_tag']}』", ha='center', va='center', fontweight='bold')
    ax.text(0.7, 0.5, f"義務(社会性)\n{so_pct}%\n『{scan['social_tag']}』", ha='center', va='center', fontweight='bold')
    
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    st.pyplot(fig)
    
    st.info(scan['deep_analysis'])
    st.subheader("💎 誠実さへの肯定")
    st.write(scan['validation'])
    
    with st.expander("⚙️ 身体コンディションによる増幅レポート"):
        st.warning(scan['hardware_effect'])
    
    st.success(f"**💡 今すぐできること:** {scan['next_step']}")
    st.markdown(f"#### 🕊️ {scan['secure_base_msg']}")
    
    if st.button("最初に戻る"): move_to(1)

