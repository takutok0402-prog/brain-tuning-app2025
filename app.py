import streamlit as st
import google.generativeai as genai

# 1. ページ設定
st.set_page_config(page_title="脳内物質デバッガー", layout="wide")

# 2. タイトル
st.title("🧠 脳内物質翻訳デバッガー")
st.markdown("---")

# 3. APIキーの設定（Secretsから取得）
if "GEMINI_API_KEY" not in st.secrets:
    st.error("APIキーが設定されていません。Streamlitの管理画面でSecretsを設定してください。")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ★修正ポイント：最新の安定版モデル「gemini-2.5-flash」に変更
# これにより404エラー（モデルが見つからない）を回避します
model = genai.GenerativeModel('gemini-2.5-flash') 

# 4. 入力エリア
user_input = st.text_area(
    "今の状況を詳しく教えてください", 
    placeholder="（例）嫌なことを考え出して止まらない/ 勉強中、別れた恋人を思い出して集中できない 等",
    help="「何が起きたか」「何について考えてしまうか」など、具体的であるほど正確な分析が可能です。"
)

st.caption("⚠️ **【禁止事項】** 氏名、住所、連絡先などの個人情報は絶対に入力しないでください。")

# 5. 実行処理
if st.button("脳内物質をデバッグする"):
    if user_input:
        with st.spinner("最新の脳科学モデルでスキャン中..."):
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
                # 生成実行
                response = model.generate_content(prompt)
                st.subheader("🛠 分析結果とデバッグ提案")
                st.markdown(response.text)
                
            except Exception as e:
                # エラーメッセージを分かりやすく日本語化
                if "429" in str(e):
                    st.error("現在、Google AIの無料利用枠（1日20回程度）を超えています。明日またお試しください。")
                elif "404" in str(e):
                    st.error("指定されたAIモデルが見つかりません。コード内のモデル名を確認してください。")
                else:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("今の状況を入力してください。")
