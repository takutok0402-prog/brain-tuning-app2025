import streamlit as st
import google.generativeai as genai

# 1. ページ設定とデザイン（正式版らしく！）
st.set_page_config(
    page_title="脳内物質デバッガー | Professional", 
    page_icon="🧠",
    layout="centered"
)

# カスタムCSSで少しプロっぽく
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 16px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🧠 脳内物質翻訳デバッガー")
st.subheader("〜 脳科学と心理学に基づく精密デバッグ 〜")
st.markdown("---")

# 2. APIキーの設定
if "GEMINI_API_KEY" not in st.secrets:
    st.error("APIキーが設定されていません。")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# 有料プランなら 'gemini-2.5-flash' が最もコスパと速度のバランスが良いです
model = genai.GenerativeModel('gemini-2.5-flash') 

# 3. ユーザー入力エリア
st.markdown("#### 📥 現在のデバッグ対象（状況）を入力してください")
user_input = st.text_area(
    label="状況詳細",
    label_visibility="collapsed",
    placeholder="（例）嫌なことについて考え続けてしま。ぼーっとしてしまい集中できない...",
    height=150,
    help="「何が原因とされるか」「どんな悩みか」を具体的に書くほど、デバッグ精度が上がります。"
)

st.warning("⚠️ **【禁止事項】** 氏名、連絡先、所属などの個人情報は入力しないでください。")

# 4. デバッグ実行
if st.button("🚀 脳内物質をデバッグ・分析する", use_container_width=True):
    if user_input:
        with st.spinner("脳内のバイオメカニズムをスキャン中..."):
            # プロンプトの更なる強化（具体性とメカニズムの徹底）
            prompt = f"""
            あなたは脳科学、神経科学、および臨床心理学の権威です。
            ユーザーの記述から現在の脳内物質バランスを推定し、具体的かつ科学的な解決策を提示してください。

            【回答の5大原則】
            1. **抽象論の排除**: 「リラックスして」「前向きに」といった言葉は一切使わないでください。
            2. **具体的アクション**: 「何を」「いつ」「どうする」か、今すぐ実行可能な物理的行動を提案してください。
            3. **バイオメカニズムの詳説**: 提案する行動が、なぜその脳内物質（ドーパミン、セロトニン、ノルアドレナリン等）や神経系（交感神経・副交感神経）に作用するのか、医学的・生物学的な裏付けを詳しく解説してください。
            4. **心理学的知見**: ユーザーが心理学を学んでいることを踏まえ、心理学的パラダイム（例：認知行動療法、マインドフルネス等）の視点も交えてください。
            5. **専門的かつ誠実なトーン**: 信頼できる専門家として回答してください。

            ユーザーの状況:
            {user_input}
            """
            
            try:
                response = model.generate_content(prompt)
                
                # 結果表示
                st.success("✅ デバッグが完了しました")
                st.markdown("---")
                st.markdown(response.text)
                
                # 免責事項（正式アプリには必須）
                st.markdown("---")
                st.caption("※本アプリのアドバイスは、脳科学の理論に基づくシミュレーションであり、医師の診断に代わるものではありません。体調不良が続く場合は医療機関を受診してください。")

            except Exception as e:
                if "429" in str(e):
                    st.error("APIの利用制限に達しました。有料プランの反映まで数分かかる場合があります。")
                else:
                    st.error(f"デバッグ中にエラーが発生しました: {e}")
    else:
        st.info("まずは今の状況を具体的に入力してください。")
