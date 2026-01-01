import streamlit as st
import google.generativeai as genai

# 1. ページ設定
st.set_page_config(
    page_title="脳内物質デバッガー | Professional", 
    page_icon="🧠",
    layout="centered"
)

# カスタムCSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 脳内物質翻訳デバッガー")
st.subheader("〜 脳科学と心理学に基づく精密デバッグ 〜")
st.markdown("---")

# 2. APIキーの設定
if "GEMINI_API_KEY" not in st.secrets:
    st.error("APIキーが設定されていません。")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash') 

# 3. ユーザー入力エリア（プレースホルダーを更新しました）
st.markdown("#### 📥 現在のデバッグ対象（状況）を入力してください")
user_input = st.text_area(
    label="状況詳細",
    label_visibility="collapsed",
    placeholder="（例）嫌なことを考え続けてしまう / ぼーっとしてしまい集中できない 等",
    height=150,
    help="具体的なエピソードや今の思考の状態を書くほど、デバッグの精度が上がります。"
)

st.warning("⚠️ **【禁止事項】** 個人情報（名前・住所など）は入力しないでください。")

# 4. デバッグ実行
if st.button("🚀 脳内物質をデバッグ・分析する", use_container_width=True):
    if user_input:
        with st.spinner("脳内のバイオメカニズムをスキャン中..."):
            prompt = f"""
            あなたは脳科学、神経科学、および臨床心理学の権威です。
            ユーザーの記述から現在の脳内物質バランスを推定し、具体的かつ科学的な解決策を提示してください。

            【回答の5大原則】
            1. 抽象論の排除: 「リラックスして」等は禁止。
            2. 具体的アクション: 今すぐ実行可能な物理的行動を提案。
            3. バイオメカニズムの詳説: なぜその行動が特定の脳内物質に作用するのか解説。
            4. 心理学的知見: 心理学的視点も交える。
            5. 専門的トーン: 信頼できる専門家として回答。

            ユーザーの状況:
            {user_input}
            """
            
            try:
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.success("✅ デバッグが完了しました")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("---")
                    st.caption("※本アプリは医師の診断に代わるものではありません。")
                else:
                    st.error("AIから有効な回答が得られませんでした。もう一度お試しください。")

            except Exception as e:
                st.error(f"デバッグ中にエラーが発生しました。詳細: {e}")
    else:
        st.info("まずは今の状況を具体的に入力してください。")
