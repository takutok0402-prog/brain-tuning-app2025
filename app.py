import streamlit as st
import google.generativeai as genai
import os

# --- 1. 初期設定 ---
st.set_page_config(page_title="SUNAO | Brain Debugger", page_icon="🧠", layout="centered")

# セッション状態の初期化
for key in ['step', 'stagnation', 'seeds', 'analysis_result', 'retry', 'discovery_count', 'smartphone_check']:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else (0 if key == 'discovery_count' else False)

# API設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def move_to(s): st.session_state.step = s

# --- STEP 1: How We Feel チェックイン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 気分のチェックイン")
    e_val = st.select_slider("⚡ エネルギー (低い ←→ 高い)", options=[-2, -1, 0, 1, 2], value=0)
    p_val = st.select_slider("🍃 心地よさ (不快 ←→ 快い)", options=[-2, -1, 0, 1, 2], value=0)
    st.button("次へ進む ➔", on_click=lambda: move_to(2), use_container_width=True)

# --- STEP 2: 停滞 ＆ スマホ依存スキャン ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳の『詰まり』をスキャン")
    
    st.session_state.stagnation = st.text_area("今抱えている悩みや不安（仕事、練習、制作など）", height=100)
    
    # 【追加機能】スマホ依存のチェック
    st.markdown("---")
    st.write("#### 📱 脳の防衛反応チェック")
    st.session_state.smartphone_check = st.checkbox("今日、スマホを無意識につい触ってしまいましたか？")
    
    if st.session_state.smartphone_check:
        st.warning("⚠️ **もしそうであれば、それは脳が『手軽に安価なドーパミン』を求めている証拠です。**")
        st.caption("脳は停滞による不足分を、手っ取り早い刺激で埋めようとしています。")

    st.markdown("---")
    st.session_state.seeds = st.text_input("本来好きなこと、つい調べちゃうこと（趣味・興味）")
    
    col1, col2 = st.columns(2)
    with col1: st.button("⬅ 戻る", on_click=lambda: move_to(1))
    with col2:
        if st.button("脳内分析 ＆ 伴走開始 ➔", use_container_width=True):
            st.session_state.discovery_count = 1
            st.session_state.retry = True
            move_to(3)

# --- STEP 3: 脳内分析 ＆ ワクワク伴走（スマホ解説付き） ---
elif st.session_state.step == 3:
    st.title("🧪 Step 3: 脳内解析 ＆ 伴走コーチング")
    
    if st.session_state.retry:
        with st.spinner("Gemini 2.5-flash があなたの報酬系を解析中..."):
            # プロンプトにスマホ逃避の解説指示を追加
            phone_status = "あり" if st.session_state.smartphone_check else "なし"
            prompt = f"""
            あなたは神経科学を極めた伴走コーチです。
            【状況】停滞：{st.session_state.stagnation} / 興味：{st.session_state.seeds} / スマホ逃避：{phone_status}
            
            以下の構成で回答してください：
            1. 【脳内物質スキャン】DA, 5-HT, NA, OT, GABA, Cortisolの状態（%）。
            2. 【スマホ逃避の解説】スマホをつい触ってしまうメカニズム（安価なドーパミンの前借り）を優しく解説。
            3. 【3つのワクワク提案】
               - 停滞に関連した『学び』（基礎トレ的）
               - 全く関係ない『遊び』（リセット的）
               - ユーザーへの『深掘り質問』（伴走）
            """
            response = model.generate_content(prompt)
            st.session_state.analysis_result = response.text
            st.session_state.retry = False

    st.markdown(f"<div style='padding:20px; border-radius:15px; background-color:#ffffff; border:1px solid #ddd;'>{st.session_state.analysis_result}</div>", unsafe_allow_html=True)
    
    # 物質バランスの視覚化
    st.divider()
    st.subheader("📊 推定バイオ・メーター")
    c1, c2 = st.columns(2)
    with c1:
        st.progress(20, text="期待値 ($DA$)")
        st.progress(80, text="ストレス負荷 ($Cortisol$)")
    with c2:
        st.progress(15, text="安定度 ($5-HT$)")
        st.progress(10, text="抑制力 ($GABA$)")
    
    st.write(f"💡 提案 {st.session_state.discovery_count}回目：脳の報酬系が動きそうですか？")
    ca, cb, cc = st.columns(3)
    with ca:
        if st.button("✨ これでいこう！"): move_to(4)
    with cb:
        if st.button("🤔 ピンとこない"):
            st.session_state.discovery_count += 1
            st.session_state.retry = True
            st.rerun()
    with cc:
        if st.button("⬅ やり直す"): move_to(2)

# --- STEP 4: 最初の一歩 ---
elif st.session_state.step == 4:
    st.title("🎁 Step 4: あなたへの処方箋")
    st.success("ワクワクのターゲットが確定しました！")
    st.write("安価なドーパミンではなく、**『質の高いワクワク』**で脳を再起動しましょう。")
    st.button("最初に戻る", on_click=lambda: move_to(1))
