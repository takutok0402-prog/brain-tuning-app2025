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
    # 以前の対話に基づき、より推論に強いモデル（フラッシュ版）を指定
    model = genai.GenerativeModel('gemini-2.5-flash')

# セッション管理
for key in ['step', 'brain_scan', 'mood_quadrant', 'selected_emotion', 'attachment_style']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- ポリヴェーガル理論に基づいた感情データベース ---
EMOTION_DB = {
    # 赤: 交感神経（闘争・逃走） - 「嫌われたくない」予測暴走
    "Red": ["心臓がバクバクする", "嫌われたくない", "頭の中で答え合わせが止まらない", "パニックになりそう", "ピリピリしている"],
    # 黄: 腹側迷走神経（活動） - 素直なエネルギー
    "Yellow": ["ワクワクしている", "いきいきしている", "集中できている", "自信がある", "やりたいことが明確"],
    # 青: 背側迷走神経（凍結） - 自己防衛としてのシャットダウン
    "Blue": ["やる気が出ない", "消えてしまいたい", "布団から出られない", "自分なんてダメだ", "感情が死んでいる"],
    # 緑: 腹側迷走神経（休息） - 安全基地・安定
    "Green": ["ほっとしている", "穏やかな気持ち", "今のままでいい", "安心している", "呼吸が深い"]
}

# --- STEP 1: 気分とアタッチメントのチェックイン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 今のあなたの『安全基地』")
    st.markdown("今の体の感覚に近い場所を選んでください。")
    
    col1, col2 = st.columns(2)
    with col1:
        energy = st.select_slider("⚡ エネルギー量", options=["動けない", "低め", "普通", "高め", "過剰"], value="普通")
    with col2:
        pleasant = st.select_slider("🍃 心の心地よさ", options=["つらい", "少し嫌", "普通", "良い", "心地よい"], value="普通")
    
    # 簡易アタッチメント傾向（以前の「不安型」などの気づきを反映）
    st.divider()
    st.markdown("##### 今、誰か（特定の人や世間）の目が気になっていますか？")
    social_filter = st.radio("（これが『社会性』の重みになります）", 
                             ["全く気にならない（素直モード）", "少し気になる", "ずっとその人のことを考えてしまう（予測ループ中）"],
                             index=1)

    # 象限判定（略：提示されたロジックを維持しつつカラー名をポリヴェーガル用語に紐付け）
    # ... (判定ロジック)
    quadrant = "Red" # 例として固定（実際は判定させる）
    
    target_emotions = EMOTION_DB[quadrant]
    selected = st.selectbox("一番近い言葉を選んでください", ["(選択してください)"] + target_emotions)
    
    if selected != "(選択してください)":
        st.session_state.mood_quadrant = quadrant
        st.session_state.selected_emotion = selected
        if st.button("脳のデバッグを開始する ➔", type="primary"):
            move_to(2)

# --- STEP 2: 脳内スキャン（岡田理論 & ポリヴェーガル統合プロンプト） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 予測マシーンの解析")
    st.markdown(f"**「{st.session_state.selected_emotion}」**という状態を分析します。")
    
    user_input = st.text_area("今、頭の中を占めている『答えの出ない問い』はありますか？", 
                            placeholder="例：なぜあんなことを言われたのか、嫌われたのではないか...")
    
    if st.button("AI調律師に接続 ➔"):
        with st.spinner("岡田尊司理論とポリヴェーガル理論を読み込み中..."):
            try:
                # 以前作成した「理論を学習させたプロンプト」をミックス
                prompt = f"""
                あなたは岡田尊司の愛着理論とポリヴェーガル理論に精通したAI調律師です。
                ユーザーの入力に基づき、脳の状態を『生存戦略』として肯定的に分析してください。

                【データ】
                - 感情: {st.session_state.selected_emotion}
                - 思考のログ: {user_input}

                【指示】
                1. 今の状態をポリヴェーガル理論（腹側/交感/背側迷走神経）で分類。
                2. 不安の原因を「脳の予測バグ（答えのないテストを解こうとしている）」として解説。
                3. 今の症状が、自分を守るための『自己防衛』であることを強調。
                4. 「社会性（他人の目）」をオフにし、「素直（自分）」を取り戻す処方箋を出す。

                【出力JSON形式】
                {{
                    "strategy_name": "生存戦略名 (例: 不安型による予測暴走)",
                    "self_defense_reason": "なぜ脳がこの状態を作ってあなたを守っているか",
                    "polyvagal_state": "腹側/交感/背側のいずれか",
                    "sociality_level": 0-100,
                    "sunao_level": 0-100,
                    "overwrite_action": "今すぐできる、社会性を遮断する物理的アクション",
                    "secure_message": "安全基地としての優しい一言"
                }}
                """
                response = model.generate_content(prompt)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.brain_scan = json.loads(cleaned)
                move_to(3)
            except Exception as e:
                st.error(f"解析エラー: {e}")

# --- STEP 3: 診断結果（新・自律の提示） ---
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
        st.write(f"今のあなたは、答えのない『他人の気持ち』というテストを解こうとしてエラーを起こしています。")
        st.success(f"**アクション:** {scan['overwrite_action']}")
    
    st.subheader("🕊️ 安全基地からのメッセージ")
    st.markdown(f"#### {scan['secure_message']}")
    
    if st.button("最初に戻って調律を続ける"):
        move_to(1)
