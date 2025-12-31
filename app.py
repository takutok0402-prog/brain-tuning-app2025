import streamlit as st
import google.generativeai as genai
import pandas as pd

# ページ設定
st.set_page_config(page_title="脳内物質デバッガー", layout="wide")

# タイトル
st.title("🧠 脳内物質翻訳デバッガー")
st.markdown("---")

# APIキーの設定（Secretsから取得）
if "GEMINI_API_KEY" not in st.secrets:
    st.error("APIキーが設定されていません。Streamlitの管理画面でSecretsを設定してください。")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # 1.5の方が無料枠が広い場合があります

# 入力エリアの改善
user_input = st.text_area(
    "今の状況を詳しく教えてください", 
    placeholder="（例）jogの時から骨盤が前傾してしまい、腰の張りが取れなくて焦っている / 心理学の試験前で、過去の失敗を思い出して集中できない 等",
    help="「何が起きたか」「何について考えてしまうか」など、具体的であるほど正確な分析が可能です。"
)

# 注意書きの追加
st.caption("⚠️ **【禁止事項】** 氏名、住所、連絡先などの個人情報は絶対に入力しないでください。")

if st.button("脳内物質をデバッグする"):
    if user_input:
        with st.spinner("脳内物質のバランスをスキャン中..."):
            # プロンプトの改善（具体的メカニズムと脱・ありきたり）
            prompt = f"""
            あなたは脳科学と心理学の専門家です。
            ユーザーの状態から、脳内物質（ドーパミン、セロトニン、ノルアドレナリン等）のバランスを分析してください。

            【回答の絶対ルール】
            1. 「ゆっくり休んで」等のありきたりな精神論は禁止。
            2. 解決策は、今すぐできる「具体的・物理的な行動」を提案すること。
            3. なぜその行動が有効なのか、どの脳内物質に作用するのかという「生物学的メカニズム」を必ず詳細に解説すること。

            ユーザーの状態:
            {user_input}
            """
            
            try:
                response = model.generate_content(prompt)
                st.subheader("🛠 分析結果とデバッグ提案")
                st.markdown(response.text)
            except Exception as e:
                if "429" in str(e):
                    st.error("現在、Google AIの無料利用枠を超えています。少し時間を置いてから再度お試しください。")
                else:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("今の状況を入力してください。")