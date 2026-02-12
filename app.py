import streamlit as st
import google.generativeai as genai
import os
import json
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- 0. 環境・表示設定 ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

st.set_page_config(page_title="SUNAO | Holistic Tuner", page_icon="🧘", layout="centered")

# APIキー設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' # 最新モデル推奨
else:
    st.error("APIキーが未設定です。")

# セッション管理
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 身体スキャン（変更なし） ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 身体スキャン")
    st.markdown("今の身体の声を丁寧に拾い上げ、チューニングの土台を作ります。")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["絶望的", "浅い", "普通", "快眠"], value="普通")
        st.session_state.fatigue_val = st.select_slider("😫 疲労度", options=["羽のよう", "普通", "重い", "泥のよう"], value="普通")
    with col2:
        st.session_state.energy_val = st.select_slider("⚡ 活性レベル", options=["静寂", "安定", "普通", "高揚", "爆発前夜"], value="普通")
        st.session_state.pleasant_val = st.select_slider("🍃 今の気分", options=["つらい", "不快", "普通", "良い", "最高"], value="普通")

    st.divider()
    st.session_state.safebase_val = st.radio("🏠 今、ここはあなたの「聖域」ですか？", ["はい", "いいえ（警戒中）"], index=0)

    if st.button("脳内ログ（一括入力）へ ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ（一括入力 & 自動仕分け） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内デフラグ")
    st.info("✨ **今、心にあるものをすべて、この箱に吐き出してください。**\nAIデバッガーが「自分軸（70%）」と「外部ノイズ（30%）」に自動で仕分けます。")
    
    # 入力欄をひとつに統合
    st.session_state.raw_input = st.text_area(
        "脳内のログをすべて書き出してください（悩み、願望、不安、今日のタスク...）", 
        height=300, 
        placeholder="例：あの時こうしてれば、、うまくいくかな、、〇〇しないと。しんどい。"
    )

    st.divider()
    
    if st.button("全エネルギーを解析・変換 ➔", type="primary"):
        if not st.session_state.raw_input:
            st.warning("何か言葉を投げ込んでください。素材がないと料理が作れません！")
        else:
            with st.spinner("デバッガーが素材を精査・仕分け中..."):
                try:
                    model = genai.GenerativeModel(model_id)
                    prompt = f"""
                    あなたは「SUNAOシステム」の最強デバッガーです。
                    ユーザーから提出された未整理の「脳内ログ」を、70:30理論に基づいて精密に仕分けなさい。

                    【仕分けルール】
                    1. 自分軸 (Internal 70%): 自分の行動、思考、五感、コントロール可能な現在と未来のタスク。
                    2. 外部軸 (External 30%): 他人の反応、過去、環境（天気など）、自分ではコントロール不可能な不安や期待。

                    【データ】
                    ユーザー入力: {st.session_state.raw_input}
                    
                    【解析任務】
                    - 入力文から「自分軸」と「外部軸」の要素を抽出しなさい。
                    - 文章全体の熱量や単語数から、現在の「外部軸（ノイズ）の脳内占有率(0-100%)」を推定しなさい。

                    【JSON構造】
                    {{
                        "daily_title": "今の状態を象徴する称号",
                        "estimated_external_occupancy": 0から100の数値,
                        "audit_report": "なぜこのように仕分けたか、デバッガーとしての短い見解",
                        "my_territory": ["自分軸に分類された項目リスト"],
                        "external_territory": ["外部軸に分類された項目リスト"],
                        "turbo_message": "外部の熱（未練や不安）を、自分を動かす燃料に変える熱い言葉",
                        "boost_action": "今日1ミリ更新するための具体的アクション",
                        "somatic_work": "今の状態に最適な身体調整（接地ワーク）"
                    }}
                    """
                    res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    st.session_state.brain_scan = json.loads(res.text)
                    # 推定された占有率をセッションに保存
                    st.session_state.external_occupancy = st.session_state.brain_scan.get('estimated_external_occupancy', 30)
                    move_to(3)
                except Exception as e: st.error(f"デバッグエラー: {e}")

# --- STEP 3: レポート（調律完了） ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 調律完了レポート")
    st.success(f"### 称号：『 {scan.get('daily_title', 'SUNAOな旅人')} 』")

    # AIが推定した占有率でグラフを表示
    ext_p = st.session_state.external_occupancy
    r = 100 - ext_p
    
    fig, ax = plt.subplots(figsize=(6, 0.8))
    ax.barh(["Axis"], [r], color="#3498db") # 自分軸
    ax.barh(["Axis"], [ext_p], left=[r], color="#e67e22") # 外部軸
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}%（あなたの領土） / 🟠 外部軸: {ext_p}%（燃やすべき燃料）")

    st.divider()
    st.subheader("🔍 デバッガーの見解")
    st.info(scan.get('audit_report', '...'))

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**🔵 あなたがコントロールできること (70%)**")
        for t in scan.get('my_territory', []): st.write(f"✅ {t}")
    with col_r2:
        st.markdown("**🟠 あなたが手放し、燃料にするもの (30%)**")
        for t in scan.get('external_territory', []): st.write(f"🔥 {t}")

    st.divider()
    st.subheader("🚀 ターボチャージャー（変換）")
    st.markdown(f"**💬 Message:**\n> {scan.get('turbo_message', '...')}")
    st.warning(f"🔥 **今日のブースト行動:** {scan.get('boost_action', '...')}")

    st.divider()
    st.subheader("🛠️ 身体スイッチ（Somatic Tuning）")
    st.write(scan.get('somatic_work', '...'))

    if st.button("機体をリセットして最初に戻る"): move_to(1)
