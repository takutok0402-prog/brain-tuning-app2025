import streamlit as st
import google.generativeai as genai
import pandas as pd
import re

import streamlit as st
import google.generativeai as genai

# --- セキュリティ対策版の設定 ---
# st.secrets からAPIキーを読み込む（コード上にはキーを書かない！）
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("APIキーが設定されていません。Streamlitの管理画面で設定してください。")git remote add origin https://github.com/takutok0402-prog/brain-tuning-app2.git

# ページ構成
st.set_page_config(page_title="Brain Tuning Assistant", page_icon="🧠", layout="wide")

# デザイン設定：漆黒の背景にネオンブルーのアクセント
st.markdown("""
    <style>
    /* 全体の背景と文字 */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
    }
    /* 入力エリアのカスタマイズ */
    .stTextArea textarea {
        background-color: #161B22;
        color: #FFFFFF;
        border: 1px solid #30363D;
        border-radius: 12px;
        font-size: 1.1rem;
    }
    /* 即効アクション用のカード（箇条書きを強調） */
    .action-card {
        background-color: #1F2937;
        border: 1px solid #30363D;
        border-left: 6px solid #58A6FF;
        padding: 24px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .action-item {
        font-size: 1.15rem;
        margin-bottom: 16px;
        list-style: none;
        display: flex;
        align-items: center;
    }
    .emoji-icon {
        font-size: 1.6rem;
        margin-right: 15px;
        background: #0D1117;
        padding: 8px;
        border-radius: 50%;
    }
    /* 見出しの色 */
    h1, h2, h3 {
        color: #58A6FF !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 脳内物質翻訳デバッガー")
st.markdown("今のしんどさを**「物質のアンバランス」**として解析し、具体的な解決策を処方します。")

# --- 2. サイドバー：モデル自動取得 ---
with st.sidebar:
    st.header("⚙️ System Status")
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = st.selectbox("AIエンジン選択", models, index=0)
        st.success("API Key: Active ✅")
    except:
        selected_model = "models/gemini-1.5-flash"
        st.warning("モデルリストの取得に失敗しました。")

# --- 3. メイン入力エリア ---
user_msg = st.text_area("現在の脳の状態を言語化してください...", 
                        placeholder="例：朝から体が重くてやる気が出ない。腰も張っているし、集中力が10分も持たない。", 
                        height=120)

if st.button("脳のスキャンを開始する", use_container_width=True):
    if not user_msg:
        st.error("解析するための入力データが必要です。")
    else:
        with st.spinner("脳内物質のデータをデコード中..."):
            try:
                model = genai.GenerativeModel(selected_model)
                
                # プロンプト：グラフ化と箇条書きを徹底させる
                prompt = f"""
                ユーザーの入力： 「{user_msg}」

                あなたは脳科学に基づき、人間の心身の状態を解析する専門家です。
                以下の形式（Markdown）に則って回答してください。

                ### 【1. 物質バランス推計】
                (現在値と理想値を「物質名: 現在, 理想」の形式で0-100で出力。必ず以下の5つを含める)
                ドーパミン: 現在値, 理想値
                セロトニン: 現在値, 理想値
                オキシトシン: 現在値, 理想値
                コルチゾール: 現在値, 理想値
                ノルアドレナリン: 現在値, 理想値

                ### 【2. 脳への処方箋（即効アクション）】
                (不足・過剰状態をリセットするための、バナナ等の食べ物や物理的な行動を「📍 項目名: 内容」の形式で3つ挙げてください)

                ---詳細解説---
                (脳科学的なメカニズムを詳しく解説)
                """
                
                response = model.generate_content(prompt)
                full_text = response.text
                
                # パース処理
                if "---詳細解説---" in full_text:
                    summary, detail = full_text.split("---詳細解説---")
                else:
                    summary, detail = full_text, "詳細データなし"

                # 数値抽出
                lines = summary.split("\n")
                chart_data = []
                for line in lines:
                    match = re.search(r"(\w+): (\d+), (\d+)", line)
                    if match:
                        name, cur, tar = match.groups()
                        chart_data.append({"物質": name, "現在値": int(cur), "理想（補給目標）": int(tar)})

                st.session_state.chart_df = pd.DataFrame(chart_data)
                st.session_state.summary = summary
                st.session_state.detail = detail

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 4. 結果表示エリア ---
if "summary" in st.session_state:
    st.divider()

    col_graph, col_action = st.columns([1.2, 1], gap="large")

    with col_graph:
        st.subheader("📊 物質バランス（現在 vs 理想）")
        if not st.session_state.chart_df.empty:
            # 視覚的な棒グラフ（これが「図」の代わりになります）
            st.bar_chart(st.session_state.chart_df, x="物質", y=["現在値", "理想（補給目標）"], color=["#58A6FF", "#00D4FF"])
            st.caption("※青色が今のあなたの状態、水色が脳が求めている理想の状態です。")
            
            
        else:
            st.info("グラフデータを生成できませんでした。")

    with col_action:
        st.subheader("⚡ 脳を調律する即効アクション")
        
        # プロンプトで指定した「📍」を元にアクションを抽出してカード化
        actions = re.findall(r"📍 (.*)", st.session_state.summary)
        
        st.markdown("<div class='action-card'>", unsafe_allow_html=True)
        if actions:
            for action in actions:
                # 食べ物や行動に合わせた絵文字の自動割り当て
                icon = "🍌" if "バナナ" in action or "食" in action else \
                       "💧" if "水" in action else \
                       "🧘" if "呼吸" in action or "休" in action else \
                       "☀️" if "光" in action or "朝" in action else \
                       "🤸" if "動" in action or "ストレッチ" in action else "✨"
                
                st.markdown(f"""
                    <div class='action-item'>
                        <span class='emoji-icon'>{icon}</span>
                        <span>{action}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write(st.session_state.summary)
        st.markdown("</div>", unsafe_allow_html=True)

    # 詳細解説（アコーディオン）
    with st.expander("💡 脳科学的なメカニズム（なぜこのアクションが必要か）"):
        st.markdown(st.session_state.detail)

    # 支援者用スペース
    st.divider()
    with st.expander("📝 支援者/自己対話用メモ"):
        st.text_area("この解析結果を元に、今の自分に必要な言葉を整えてください。", 
                     value="今のしんどさは脳内物質の影響だとわかった。まずは焦らずに上記のアクションを試してみよう。", height=80)
        if st.button("送信（ログ保存）"):
            st.balloons()