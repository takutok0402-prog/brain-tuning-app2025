import streamlit as st
import google.generativeai as genai
import os

# 1. ページ設定
st.set_page_config(
    page_title="脳内物質デバッガー | SUNAO Professional", 
    page_icon="🧠",
    layout="wide"
)

# --- 2. APIキーの設定（完全修正版を統合） ---
# st.secretsを直接触らず、まず環境変数(os.getenv)をチェックする
api_key = os.getenv("GEMINI_API_KEY")

# 環境変数にない場合のみ、例外処理を挟んでst.secretsを見に行く
if not api_key:
    try:
        # Streamlit Cloud環境用の処理
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        # どちらにもない場合はエラーを表示
        api_key = None

if not api_key:
    st.error("APIキーが設定されていません。Renderの'Environment'設定、またはSecretsを確認してください。")
    st.stop()

# 鍵を適用
genai.configure(api_key=api_key)

# 最新モデルの指定
model = genai.GenerativeModel('gemini-2.5-flash')


# セッション状態の初期化
for key in ['mode', 'show_result', 'result_text']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'mode' else (False if key == 'show_result' else "")

# 3. デザインCSS
st.markdown("""
    <style>
    .report-card { padding: 25px; border-radius: 15px; background-color: #ffffff; border-left: 10px solid #4A90E2; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4CAF50, #8BC34A); }
    </style>
    """, unsafe_allow_html=True)

# 4. メインUI
st.title("🧠 脳内物質翻訳デバッガー")
st.subheader("〜 あなたの『直（すなお）』な状態を取り戻すための精密調律システム 〜")

user_input = st.text_area("今の気分や、抱えているモヤモヤを具体的に教えてください", height=120, placeholder="（例）DNS設定が通らず、期待と不安で集中できない...")

if st.button("🚀 フル・スキャニングを実行", use_container_width=True):
    if user_input:
        with st.spinner("脳内のバイオネットワークを解析中..."):
            prompt = f"""
            あなたは神経科学の権威です。以下の状況を、脳内物質バランスとネットワークの観点から簡単に分析してください。
            【分析必須項目】
            - DA, 5-HT, NA, OT, GABA, Endorphin, Cortisol の各状態（%推測）。
            - DMN（内省）の暴走度、TPN（実行）の活性度。
            - どちらのデバッグルート（強制リセット or ディープ調律）が「直（すなお）」な解決になるか。
            状況: {user_input}
            """
            try:
                response = model.generate_content(prompt)
                st.session_state.result_text = response.text
                st.session_state.show_result = True
            except Exception as e:
                st.error(f"モデル接続エラー: {e}。モデル名を変更して再試行してください。")
    else:
        st.info("状況を入力してください。")

# 5. 解析結果とビジュアル表示
if st.session_state.show_result:
    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🔍 脳内デバッグ報告書")
        st.markdown(f"<div class='report-card'>{st.session_state.result_text}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📊 推定バイオ・ステータス")
        # 物質スキャン（セロトニン・ドーパミン以外も含む）
        st.progress(30, text="安定：セロトニン ($5-HT$)")
        st.progress(20, text="快感：ドーパミン ($DA$)")
        st.progress(85, text="覚醒：ノルアドレナリン ($NA$)")
        st.progress(15, text="絆：オキシトシン ($OT$)")
        st.progress(10, text="抑制：$GABA$")
        st.progress(95, text="負荷：コルチゾール")
        
        st.divider()
        st.write("**🧠 ネットワーク・バランス**")
        st.markdown("🔴 **$DMN$（反芻思考）**: 活性過多")
        st.markdown("⚪ **$TPN$（外部集中）**: 低下中")

    # 6. ルート選択
    st.markdown("### 💡 どちらのデバッグを開始しますか？")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 強制リセット（外へ集中）"): st.session_state.mode = 'reset'
    with c2:
        if st.button("🌿 ディープ・調律（内を癒やす）"): st.session_state.mode = 'tuning'

# 7. モード別メニュー
if st.session_state.mode:
    st.markdown("---")
    mode = st.session_state.mode
    st.success(f"【{'強制リセット' if mode=='reset' else 'ディープ・調律'}】メニューをロードしました。")
    
    tab1, tab2, tab3 = st.tabs(["🎵 音楽", "📺 動画", "🚶 身体活動"])
    with tab1:
        if mode == 'reset':
            st.write("🔥 **爆揚（ドーパミン）リスト**")
            st.video("https://www.youtube.com/watch?v=scXpP77p7no") # オレンジ/SPYAIR
        else:
            st.write("💧 **浄化（Progress）リスト**")
            st.video("https://www.youtube.com/watch?v=J7VM_2llOcg") # Progress/スガシカオ
    with tab2:
        st.write("箱根駅伝、大谷選手、新幹線のCMなど、視覚から脳を調律します。")
    with tab3:
        st.write("ピラティス、散歩、お尻の筋肉ほぐしなど、身体からのアプローチ。")

st.markdown("---")
st.caption("本内容は医学的診断ではありません。入力データは安全な環境で処理されています。")
