import streamlit as st
import google.generativeai as genai
import os

# --- 1. ページ設定・デザイン注入 ---
st.set_page_config(page_title="脳内物質デバッガー | SUNAO", page_icon="🧠", layout="wide")

# カスタムCSSで「アプリ感」を出す
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5em; background-color: #4A90E2; color: white; font-weight: bold; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .report-box { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

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
model = genai.GenerativeModel('gemini-1.5-flash')

# セッション状態の初期化
if 'mode' not in st.session_state: st.session_state.mode = None
if 'show_result' not in st.session_state: st.session_state.show_result = False
if 'result_text' not in st.session_state: st.session_state.result_text = ""

# --- 3. メインレイアウト ---
st.title("🧠 脳内物質翻訳デバッガー")
st.caption("〜 あなたの『直（すなお）』な状態を取り戻すための精密調律システム 〜")

with st.container():
    st.markdown("#### 📥 現在の脳内状況をスキャン")
    user_input = st.text_area("今の気分や、抱えているモヤモヤを具体的に教えてください", height=120, placeholder="（例）DNS設定で44時間待っていて、期待と不安が入り混じっている...")

    if st.button("🚀 フル・スキャニングを実行する"):
        if user_input:
            with st.spinner("脳内のバイオネットワークを解析中..."):
                prompt = f"""
                あなたは神経科学と臨床心理学の権威です。以下の状況を、5-HT, DA, NA, OT, GABA, Cortisolのバランスと、DMN/TPNの観点から詳細にデバッグ分析してください。
                最後に、なぜ『爆揚』か『浄化』が必要なのかを科学的に結論づけてください。
                状況: {user_input}
                """
                try:
                    response = model.generate_content(prompt)
                    st.session_state.result_text = response.text
                    st.session_state.show_result = True
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# --- 4. 解析結果の表示 ---
if st.session_state.show_result:
    st.markdown("---")
    col_rep, col_stat = st.columns([2, 1])

    with col_rep:
        st.markdown("### 🔍 脳内デバッグ報告書")
        st.markdown(f"<div class='report-box'>{st.session_state.result_text}</div>", unsafe_allow_html=True)

    with col_stat:
        st.markdown("### 📊 物質バランス")
        st.progress(25, text="5-HT (セロトニン)")
        st.progress(15, text="DA (ドーパミン)")
        st.progress(85, text="NA (ノルアド)")
        st.progress(95, text="Cortisol (ストレス)")
        st.divider()
        st.write("**推奨ネットワーク切り替え**")
        st.info("DMN（内省）→ TPN（集中）への移行を推奨")

    st.markdown("### 💡 どちらのデバッグルートを選択しますか？")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 強制リセット（外へ集中）"): st.session_state.mode = 'reset'
    with c2:
        if st.button("🌿 ディープ・調律（内を癒やす）"): st.session_state.mode = 'tuning'

# --- 5. モード別：厳選処方箋 ---
if st.session_state.mode:
    st.markdown("---")
    mode = st.session_state.mode
    st.subheader("💊 あなた専用の処方箋（Prescription）")
    
    tab1, tab2, tab3 = st.tabs(["🎵 音楽デバッグ", "📺 視覚デバッグ", "🚶 身体アプローチ"])
    
    with tab1:
        if mode == 'reset':
            st.write("🔥 **爆揚（ドッパドッパドーパミン）14選**")
            songs = ["オレンジ / SPYAIR", "シュガーソングとビターステップ / UNISON SQUARE GARDEN", "The Beginning / ONE OK ROCK", "アイドル / YOASOBI"]
            for song in songs: st.checkbox(song, key=song)
            st.video("https://www.youtube.com/watch?v=scXpP77p7no") # オレンジ
        else:
            st.write("💧 **浄化（Progress）9選**")
            songs = ["Progress / スガシカオ", "明日はきっといい日になる / 高橋優", "虹 / 高橋優", "ファンファーレ / sumika"]
            for song in songs: st.checkbox(song, key=song)
            st.video("https://www.youtube.com/watch?v=J7VM_2llOcg") # Progress

    with tab2:
        if mode == 'reset':
            st.write("🏆 **自分にもできると思える勇気の映像**")
            st.write("・箱根駅伝：限界突破のシーン\n・大谷翔平：挑戦の軌跡")
        else:
            st.write("💖 **温かさに触れて浄化される映像**")
            st.write("・JR東海：新幹線CM（会いにいこう）\n・箱根駅伝：襷がつなぐ絆の物語")

    with tab3:
        st.write("🏃 **フィジカル・デバッグ**")
        if mode == 'reset': st.write("・1分間早歩き\n・骨盤を起こすピラティス")
        else: st.write("・深呼吸と骨盤の安定\n・お尻ほぐしストレッチ")

# --- 7. フッター（免責事項） ---
st.markdown("---")
st.caption("本内容は医学的診断ではありません。入力データはAIの学習に利用されない安全な環境で処理されています。")
