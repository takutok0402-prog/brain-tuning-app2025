import streamlit as st
import google.generativeai as genai

# 1. ページ設定（最も標準的な設定）
st.set_page_config(page_title="脳内物質デバッガー", page_icon="🧠")

st.title("🧠 脳内物質翻訳デバッガー")
st.write("脳科学と心理学に基づく精密分析。具体的な行動を提案します。")

# 2. APIキーの設定
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlitの管理画面で『GEMINI_API_KEY』を設定してください。")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 有料プランで最も推奨される最新モデル
model = genai.GenerativeModel('gemini-2.5-flash') 

# 3. 入力エリア（エラーが起きにくいシンプルな設定に変更）
user_input = st.text_area(
    "今の状況（悩み、思考、体調など）を教えてください", 
    placeholder="（例）嫌なことを考え続けてしまう / ぼーっとしてしまい集中できない 等",
    height=150
)

st.caption("⚠️ 個人情報は入力しないでください。")

# 4. 実行処理
if st.button("デバッグを開始する"):
    if user_input:
        with st.spinner("分析中..."):
            # 有料プランのメリット（データ非学習・回数制限緩和）を活かす高精度指示
            prompt = f"""
            あなたは脳科学、神経科学、および心理学の権威です。
            以下の状況から脳内物質バランスを分析し、改善策を提示してください。

            【ルール】
            1. ありきたりな精神論（頑張れ、休め等）は禁止。
            2. 「今すぐできる具体的な物理的行動」を提案すること。
            3. その行動がどの脳内物質にどう作用するか、生物学的メカニズムを詳しく解説すること。

            状況: {user_input}
            """
            
            try:
                response = model.generate_content(prompt)
                
                if response.text:
                    st.subheader("🛠 分析結果と提案")
                    st.markdown(response.text)
                    st.divider()
                with st.expander("💡 解決策に納得がいかない、またはもっと深く相談したい方へ"):
    st.write("AIの提案がしっくりこない場合や、個別の事情を直接話したい場合は、以下の方法をお試しください。")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("別の視点から再分析する"):
            # セッション状態をクリアして、入力を促すか自動で再生成
            st.info("さらに具体的なエピソードを書き足して、もう一度『デバッグを開始』してみてください。")
    
    with col2:
        # 直接問い合わせ（解決サービスへの入口）
        st.link_button("直接相談・問い合わせる", "https://your-contact-link.com")
                    st.caption("※本内容は医学的診断ではありません。")
                else:
                    st.error("AIからの返答が空でした。もう一度送信してください。")

            except Exception as e:
                st.error(f"エラーが発生しました。時間を置いてお試しください。({e})")
    else:
        st.info("分析したい内容を入力してください。")

