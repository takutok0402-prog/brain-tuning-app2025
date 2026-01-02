import streamlit as st
import google.generativeai as genai

# 1. ページ設定
st.set_page_config(
    page_title="脳内物質デバッガー | Professional", 
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 脳内物質翻訳デバッガー")
st.subheader("〜 脳科学と心理学に基づく精密デバッグ 〜")
st.markdown("---")

import os  # ファイルの冒頭（import streamlit as st の下あたり）に追加

# --- 2. APIキーの設定（修正版） ---
# Renderの環境変数(os.getenv)を優先し、なければStreamlitのSecrets(st.secrets)を探す
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("APIキーが設定されていません。RenderのEnvironment Variables、またはSecretsを確認してください。")
        st.stop()

genai.configure(api_key=api_key)

# 有料プラン（従量課金）で最も推奨される最新モデル
model = genai.GenerativeModel('gemini-2.5-flash') 

# 3. ユーザー入力エリア
st.markdown("#### 📥 現在のデバッグ対象（状況）を入力してください")
user_input = st.text_area(
    label="状況詳細",
    label_visibility="collapsed",
    placeholder="（例）嫌なことを考え続けてしまう / ぼーっとしてしまい集中できない 等",
    height=150
)

st.warning("⚠️ **【禁止事項】** 個人情報は入力しないでください。")

# 4. デバッグ実行
if st.button("🚀 脳内物質をデバッグ・分析する", use_container_width=True):
    if user_input:
        with st.spinner("脳内のバイオメカニズムをスキャン中..."):
            # プロンプト：「直（すなお）」を軸にした静と動の2パターン提示
            prompt = f"""
            あなたは脳科学、神経科学、および臨床心理学の権威であり、ユーザーが自分自身の「直（すなお）」な状態に立ち返るのを支援するパートナーです。
            
            【基本理念：直（すなお）】
            「直」とは、今の自分の状態を脚色せず、良い・悪いの判断を脇に置いて、ありのままに認めることです。
            
            【回答の構成ルール】
            1. 現状の脳内スキャン（分析）: 脳内物質バランスを科学的に言語化。
            2. 「静（せい）」のデバッグ（ゆっくり休む）: 脳を停止させ、クリーンアップするアプローチ（DMNの起動）。
            3. 「動（どう）」のデバッグ（アクションを起こす）: 報酬系を再起動し、エンジンをかけるアプローチ。
            4. メカニズムの科学的詳説: なぜその行動が特定の物質に作用するのか解説。
            5. 「直（すなお）」な感覚への問いかけ: どちらがしっくりくるかユーザーに確認。

            状況: {user_input}
            """
            
            try:
                # 生成実行
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.success("✅ デバッグが完了しました")
                    st.markdown("---")
                    st.markdown(response.text) # AIの回答を表示
                    
                    # --- エスケープハッチ（不満・問い合わせボタン） ---
                    st.divider() 
                    with st.expander("💡 提案に納得がいかない、または直接相談したい方へ"):
                        st.write("AIの提案が『直（すなお）』な感覚としっくりこない場合は、以下のオプションをご利用ください。")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("別の視点で再分析する"):
                                st.info("状況を詳しく書き足して、もう一度ボタンを押してみてください。")
                        with col2:
                            # 解決（出口）サービスへのリンク
                            st.link_button("直接問い合わせ・専門家に相談", "https://your-contact-link.com")
                    
                    st.markdown("---")
                    # エラー箇所を確実に一行で記述し、閉じカッコを修正
                    st.caption("本内容は医学的診断ではありません。入力データはAIの学習に利用されない安全な環境で処理されています。")
                    # ----------------------------------------------
                else:
                    st.error("AIから有効な回答が得られませんでした。")

            except Exception as e:
                st.error(f"デバッグ中にエラーが発生しました。時間を置いて再度お試しください。 (詳細: {e})")
    else:
        st.info("まずは今の状況を具体的に入力してください。")
        




