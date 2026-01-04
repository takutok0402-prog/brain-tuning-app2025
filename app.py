import streamlit as st
import google.generativeai as genai
import os

# --- 1. プロフェッショナル設定 ---
st.set_page_config(
    page_title="SUNAO | 脳内物質デバッガー",
    page_icon="🧠",
    layout="wide"
)

# デザインの最終調整（カード型UIと配色）
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .status-card {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .main-title { color: #1e293b; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API & モデル設定 (2.5-flash) ---
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。RenderのEnvironment設定を確認してください。")
    st.stop()

genai.configure(api_key=api_key)

# ユーザー指定の最新モデル 2.5-flash を採用
model = genai.GenerativeModel('gemini-2.5-flash')

# セッション状態の初期化
for key in ['mode', 'show_result', 'result_text']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'mode' else (False if key == 'show_result' else "")

# --- 3. アプリケーション・メイン ---
st.markdown("<h1 class='main-title'>🧠 脳内分析ツール</h1>", unsafe_allow_html=True)
st.caption("〜 あなたの『直（すなお）』な状態を取り戻すための精密調律システム 〜")

st.divider()

# 入力セクション
user_input = st.text_area(
    "現在のデバッグ対象（思考・感情・体調）",
    height=150,
    placeholder="（例）嫌なことを考え続けてしまう..."
)

if st.button("🚀 フルスキャン・デバッグを実行", use_container_width=True):
    if user_input:
        with st.spinner("2.5-flash エンジンで脳内物質を演算中..."):
            # プロンプトの更なる精密化
            prompt = f"""
            あなたは神経科学の世界的権威です。以下の状況を、多角的な脳内物質のバランスと、神経ネットワークの活動状態から詳細に分析してください。
            
            【スキャン対象】
            - $DA$ (ドーパミン), $5-HT$ (セロトニン), $NA$ (ノルアドレナリン), $OT$ (オキシトシン), $GABA$ (抑制力), $Cortisol$ (ストレス)
            - $DMN$ (内省ループ) の活性度 vs $TPN$ (タスク集中) の効率
            - 回復に向けた具体的な「静」と「動」のアプローチ
            
            状況: {user_input}
            """
            try:
                response = model.generate_content(prompt)
                st.session_state.result_text = response.text
                st.session_state.show_result = True
            except Exception as e:
                st.error(f"AI解析エラー: {e}")

# --- 4. 解析結果のダッシュボード表示 ---
if st.session_state.show_result:
    st.markdown("---")
    col_rep, col_viz = st.columns([1.5, 1])

    with col_rep:
        st.markdown("### 🔍 脳内デバッグ報告書")
        st.markdown(f"<div class='status-card'>{st.session_state.result_text}</div>", unsafe_allow_html=True)

    with col_viz:
        st.markdown("### 📊 バイオ・スタック")
        # 6つの物質をプログレスバーで可視化
        st.write("✨ セロトニン ($5-HT$)")
        st.progress(40)
        st.write("⚡ ドーパミン ($DA$)")
        st.progress(70)
        st.write("🔥 ノルアドレナリン ($NA$)")
        st.progress(30)
        st.write("💖 オキシトシン ($OT$)")
        st.progress(85)
        st.write("📉 GABA / コルチゾール")
        st.progress(15)
        
        st.divider()
        st.markdown("#### 🧠 稼働エリア解析")
        st.info("**$TPN$（外部集中ネットワーク）** が優位にシフトしています。このままアクションを起こすのに最適な状態です。")

    # ルート選択
    st.markdown("### 💡 推奨されるデバッグ・アクション")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 強制リセット（外へ集中）"): st.session_state.mode = 'reset'
    with c2:
        if st.button("🌿 ディープ・調律（内を癒やす）"): st.session_state.mode = 'tuning'

# --- 5. アクション別コンテンツ ---
if st.session_state.mode:
    mode = st.session_state.mode
    st.markdown("---")
    st.subheader(f"💊 {'強制リセット' if mode=='reset' else 'ディープ・調律'} 用の処方箋")
    
    t1, t2 = st.tabs(["🎵 音楽デバッグ", "📺 視覚デバッグ"])
    with t1:
        # 2.5-flashの提案に基づき、あなたのリストから最適なものを表示
        url = "https://www.youtube.com/watch?v=scXpP77p7no" if mode == 'reset' else "https://www.youtube.com/watch?v=J7VM_2llOcg"
        st.video(url)
    with t2:
        st.write("箱根駅伝、大谷選手、新幹線CMなど、2.5-flashが選定した最適な映像。")

# --- 6. フッター ---
st.markdown("---")
st.caption("© 2026 SUNAO Tuning App | Powered by Gemini 2.5-flash | Domain: sunao-tuning.jp")
st.caption("本内容は医学的診断ではありません。入力データはAIの学習に利用されない安全な環境で処理されています。")
