import streamlit as st
import google.generativeai as genai
import os
import json

# --- 1. 設定とデータベース ---
st.set_page_config(page_title="SUNAO | Attachment Tuning", page_icon="🧘", layout="centered")

# API設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # モデル名は環境に合わせて調整（2.5-flashが動作するならそのままでOK）
    model_name = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション管理
for key in ['step', 'brain_scan', 'selected_emotion', 'social_filter_val']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- 感情データベース ---
EMOTION_DB = {
    "Red": ["心臓がバクバクする", "嫌われたくない", "頭の中で答え合わせが止まらない", "パニックになりそう", "ピリピリしている"],
    "Yellow": ["ワクワクしている", "いきいきしている", "集中できている", "自信がある", "やりたいことが明確"],
    "Blue": ["やる気が出ない", "消えてしまいたい", "布団から出られない", "自分なんてダメだ", "感情が死んでいる"],
    "Green": ["ほっとしている", "穏やかな気持ち", "今のままでいい", "安心している", "呼吸が深い"]
}

# --- STEP 1: 気分とアタッチメントのチェックイン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 今のあなたの『安全基地』")
    st.markdown("今の体の感覚に近い場所を選んでください。")
    
    col1, col2 = st.columns(2)
    with col1:
        energy_opts = ["動けない", "低め", "普通", "高め", "過剰"]
        energy = st.select_slider("⚡ エネルギー量", options=energy_opts, value="普通")
    with col2:
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "心地よい"]
        pleasant = st.select_slider("🍃 心の心地よさ", options=pleasant_opts, value="普通")
    
    st.divider()
    st.markdown("##### 今、誰か（特定の人や世間）の目が気になっていますか？")
    social_filter = st.radio("（これが『社会性』の重みになります）", 
                             ["全く気にならない（素直モード）", "少し気になる", "ずっとその人のことを考えてしまう（予測ループ中）"],
                             index=1)
    st.session_state.social_filter_val = social_filter

    # --- 象限判定ロジックの実装 ---
    e_idx = energy_opts.index(energy) - 2
    p_idx = pleasant_opts.index(pleasant) - 2
    
    if e_idx >= 0 and p_idx < 0: quadrant = "Red"
    elif e_idx >= 0 and p_idx >= 0: quadrant = "Yellow"
    elif e_idx < 0 and p_idx < 0: quadrant = "Blue"
    else: quadrant = "Green"
    
    target_emotions = EMOTION_DB[quadrant]
    selected = st.selectbox(f"今の感覚に近い言葉（{quadrant}エリア）", ["(選択してください)"] + target_emotions)
    
    if selected != "(選択してください)":
        st.session_state.selected_emotion = selected
        if st.button("脳のデバッグを開始する ➔", type="primary"):
            move_to(2)

# --- STEP 2: 脳のデバッグ ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 予測マシーンの解析")
    st.markdown(f"**「{st.session_state.selected_emotion}」**という状態を分析します。")
    
    user_input = st.text_area(
        "今、頭の中を占めている『答えの出ない問い』はありますか？", 
        placeholder="例：なぜあんなことを言われたのか、嫌われたのではないか...",
        key="current_user_input"
    )
    
    if st.button("AI調律師に接続 ➔"):
        with st.spinner("岡田尊司理論とポリヴェーガル理論を照合中..."):
            try:
                generation_config = {"response_mime_type": "application/json"}
                structured_model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash'
                    generation_config=generation_config,
                    system_instruction="あなたは岡田尊司の愛着理論とポリヴェーガル理論の専門家です。ユーザーの不安を『生存のための自己防衛』として肯定し、脳の予測バグを修正するための解析を行ってください。"
                )

                prompt = f"""
                【解析対象】
                - 感情表現: {st.session_state.selected_emotion}
                - 社会性の重み: {st.session_state.social_filter_val}
                - 思考ログ: {user_input}

                【解析ガイドライン】
                - 「嫌われたくない」という社会性が「素直な本能」を上回っているか判定してください。
                - 不安の正体を「脳が答えのないテスト（他人の気持ち）を解こうとして起こした予測バグ」として解説してください。
                - ポリヴェーガル理論に基づき、現在どの神経系（腹側/交感/背側）が優位か特定してください。

                【出力JSON構造】
                {{
                    "strategy_name": "生存戦略名",
                    "self_defense_reason": "脳があなたを守ろうとしている理由",
                    "polyvagal_state": "腹側/交感/背側",
                    "sociality_level": 0-100,
                    "sunao_level": 0-100,
                    "overwrite_action": "今すぐできる、社会性を遮断する物理的アクション",
                    "secure_message": "安全基地（岡田先生的）からの言葉"
                }}
                """
                response = structured_model.generate_content(prompt)
                # markdownの装飾を除去してパース
                res_text = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.brain_scan = json.loads(res_text)
                move_to(3)

            except Exception as e:
                st.error(f"解析中にエラーが発生しました: {e}")

    if st.button("← 戻る"): move_to(1)

# --- STEP 3: 診断結果 ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: あなたの脳の生存戦略")
    
    st.subheader(f"🛡️ {scan['strategy_name']}")
    st.info(f"**【脳の言い分】** {scan['self_defense_reason']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("社会性（他人の目）", f"{scan['sociality_level']}%")
        st.progress(scan['sociality_level']/100)
    with col2:
        st.metric("素直（本来の自分）", f"{scan['sunao_level']}%")
        st.progress(scan['sunao_level']/100)
        
    st.divider()
    st.markdown(f"**現在のアクティブ神経系:** `{scan['polyvagal_state']}神経系`")
    
    with st.expander("💡 脳のバグを修正する（Overwrite）"):
        st.write("脳は今、予測不能な『他人の心』という問題を解こうとして熱暴走しています。")
        st.success(f"**今すぐやるべきこと:** {scan['overwrite_action']}")
    
    st.subheader("🕊️ 安全基地からのメッセージ")
    st.markdown(f"#### {scan['secure_message']}")
    
    if st.button("最初に戻って調律を続ける"): move_to(1)
