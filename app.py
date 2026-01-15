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

# --- STEP 2 内の解析ロジック修正案 ---
if st.button("AI調律師に接続 ➔"):
    if not api_key:
        st.error("APIキーが設定されていません")
    else:
        with st.spinner("理論データを照合中..."):
            try:
                # JSONモードを強制する設定
                generation_config = {
                    "response_mime_type": "application/json",
                }
                
                # モデルの再定義（システム指示と設定を追加）
                structured_model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash',
                    generation_config=generation_config,
                    system_instruction="あなたは岡田尊司の愛着理論とポリヴェーガル理論の専門家です。必ず指定されたJSONフォーマットのみを出力してください。"
                )

                prompt = f"""
                ユーザーの「{st.session_state.selected_emotion}」という状態を分析してください。
                補足: {user_input}

                以下の構造のJSONで出力してください：
                {{
                    "strategy_name": "生存戦略名",
                    "self_defense_reason": "自己防衛の理由",
                    "polyvagal_state": "自律神経の状態",
                    "sociality_level": 0-100,
                    "sunao_level": 0-100,
                    "overwrite_action": "物理的アクション",
                    "secure_message": "安全基地の言葉"
                }}
                """
                
                response = structured_model.generate_content(prompt)
                
                # エラー対策：レスポンスが空でないか確認
                if response.text:
                    st.session_state.brain_scan = json.loads(response.text)
                    move_to(3)
                else:
                    st.error("AIからの返答が空でした。もう一度試してください。")

            except json.JSONDecodeError as je:
                st.error(f"JSON解析エラー: AIの出力形式が正しくありません。出力内容: {response.text}")
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")
                
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

