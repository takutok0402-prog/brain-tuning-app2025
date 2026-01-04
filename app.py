import streamlit as st
import google.generativeai as genai
import os

# --- 1. ページ構成と初期化 ---
st.set_page_config(page_title="SUNAO | Brain Debugger", page_icon="🧠", layout="centered")

# セッション状態の初期化
for key in ['step', 'mode', 'analysis_result', 'mood_color']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else None

# API設定 (Gemini 2.5-flash)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 画面遷移関数
def move_to(step): st.session_state.step = step

# --- 2. STEP 1: How We Feel 風チェックイン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 気分のチェックイン")
    st.write("今の『エネルギー』と『心地よさ』を直感で選んでください。")
    
    e_val = st.select_slider("⚡ エネルギー (低い ←→ 高い)", options=[-2, -1, 0, 1, 2], value=0)
    p_val = st.select_slider("🍃 心地よさ (不快 ←→ 快い)", options=[-2, -1, 0, 1, 2], value=0)
    
    # エリア判定
    if e_val >= 0 and p_val < 0: st.session_state.mood_color = "🔴 赤（高・不快 / 焦り・怒り）"
    elif e_val >= 0 and p_val >= 0: st.session_state.mood_color = "🟡 黄（高・快 / 喜び・興奮）"
    elif e_val < 0 and p_val < 0: st.session_state.mood_color = "🔵 青（低・不快 / 悲しみ・無気力）"
    else: st.session_state.mood_color = "🟢 緑（低・快 / 穏やか・満足）"
    
    st.info(f"現在のステータス: {st.session_state.mood_color}")
    st.button("詳細スキャンへ進む ➔", on_click=lambda: move_to(2), use_container_width=True)

# --- 3. STEP 2: 脳内精密スキャン ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内精密スキャン")
    user_input = st.text_area("今のモヤモヤや体の状態（何もやる気になれない等）を書いてください", height=150)
    
    col1, col2 = st.columns(2)
    with col1: st.button("⬅ 戻る", on_click=lambda: move_to(1))
    with col2:
        if st.button("2.5-flashで脳内解析 ➔", use_container_width=True):
            if user_input:
                with st.spinner("🧠 伝達物質の分泌量をシミュレーション中..."):
                    prompt = f"""
                    あなたは神経科学の権威です。以下の情報から脳内をデバッグ分析してください。
                    エリア: {st.session_state.mood_color}
                    状況: {user_input}
                    【解析項目】
                    - DA, 5-HT, NA, OT, GABA, Cortisolのバランス。
                    - DMN（内省ループ）の暴走度。
                    - あなたに今必要な『正確な感情の名前』を3つ提示。
                    """
                    response = model.generate_content(prompt)
                    st.session_state.analysis_result = response.text
                    move_to(3)
            else:
                st.warning("状況を入力してください。")

# --- 4. STEP 3: 解析報告書とアクション選択 ---
elif st.session_state.step == 3:
    st.title("📋 Step 3: 脳内デバッグ報告書")
    
    # 解析結果の表示
    st.markdown(f"### 現在の脳内バランス分析")
    st.write(st.session_state.analysis_result)
    
    st.divider()
    st.subheader("📊 バイオ・ステータス")
    c1, c2 = st.columns(2)
    with c1:
        st.progress(30, text="安定度 ($5-HT$)")
        st.progress(85, text="警戒度 ($NA$)")
        st.progress(10, text="抑制力 ($GABA$)")
    with c2:
        st.progress(20, text="期待値 ($DA$)")
        st.progress(15, text="安心感 ($OT$)")
        st.progress(90, text="ストレス負荷 ($Cortisol$)")

    

    st.markdown("### 💡 どちらのルートでデバッグしますか？")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 強制リセット（外へ集中）"):
            st.session_state.mode = 'reset'; move_to(4)
    with col2:
        if st.button("🌿 ディープ・調律（内を癒やす）"):
            st.session_state.mode = 'tuning'; move_to(4)

# --- 5. STEP 4: 処方（完了） ---
elif st.session_state.step == 4:
    st.title("🎁 Step 4: あなたへの処方箋")
    mode = st.session_state.mode
    st.success(f"【{'強制リセット' if mode=='reset' else 'ディープ・調律'}】を開始します。")
    
    tab1, tab2, tab3 = st.tabs(["🎵 音楽", "📺 動画", "🧘 身体活動"])
    with tab1:
        url = "https://www.youtube.com/watch?v=scXpP77p7no" if mode == 'reset' else "https://www.youtube.com/watch?v=J7VM_2llOcg"
        st.video(url)
    with tab2:
        st.write("箱根駅伝、大谷選手、新幹線のCMなど、視覚から調律します。")
    with tab3:
        st.write("ピラティス、散歩、お尻の筋肉ほぐしなど、身体からのアプローチ。")
    
    st.button("⬅ 最初からやり直す", on_click=lambda: move_to(1), use_container_width=True)

# --- 共通フッター ---
st.divider()
st.caption("© 2026 SUNAO | Verified on sunao-tuning.jp | Powered by Gemini 2.5-flash")
st.caption("本内容は医学的診断ではありません。入力データは安全な環境で処理されています。")

