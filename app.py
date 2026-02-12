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
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが未設定です。")

# セッション管理
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 身体スキャン ---
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

    if st.button("脳内ログへ ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ & 70%エンジン ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内デフラグ & 70%強化")
    
    # メイン入力
    st.subheader("1. 脳内ログの一括出力")
    st.info("✨ 心にあるものをすべて吐き出してください。AIが自動で仕分けます。")
    st.session_state.raw_input = st.text_area(
        "感情、悩み、願望、不安、など...", 
        height=200, 
        placeholder="例：なんかモヤモヤする。しんどい。あの時こうしてれば、、うまくいくかな、、"
    )

    st.divider()

    # 任意入力：自分軸のガソリン
    st.subheader("2. あなたの中にある幸せ（任意）")
    st.caption("好きなこと、趣味、集中できること。これらがあなたの幸せの軸になります。")
    st.session_state.likes_input = st.text_input(
        "好きなこと・趣味・なりたい自分", 
        placeholder="例：映画、温泉、料理、英語ができる自分、筋トレして強い自分"
    )

    if st.button("全エネルギーを解析・変換 ➔", type="primary"):
        if not st.session_state.raw_input:
            st.warning("まずは脳内のログを吐き出してください。")
        else:
            with st.spinner("デバッガーが領土を精査中..."):
                try:
                    model = genai.GenerativeModel(model_id)
                    prompt = f"""
                    あなたは「SUNAOシステム」の最強デバッガーです。
                    
                    【解析ルール】
                    1. 70:30仕分け: ユーザーの「脳内ログ」から、自分軸(70%)と外部軸(30%)を自動抽出せよ。
                    2. 占有率推定: 外部軸のノイズが脳を占領している割合(0-100)を数値化せよ。
                    3. 70%強化戦略: 
                       - ユーザーの「好きなこと/趣味」が入力されている場合：それを用いた具体的な「ブースト行動」を処方せよ。
                       - 入力がない場合：身体感覚（五感）を使った「接地ワーク」を優先せよ。

                    【データ】
                    脳内ログ: {st.session_state.raw_input}
                    好きなこと/趣味: {st.session_state.likes_input}
                    
                    【JSON構造】
                    {{
                        "daily_title": "称号",
                        "estimated_external_occupancy": 0から100の数値,
                        "audit_report": "仕分けの見解",
                        "my_territory": ["自分軸リスト"],
                        "external_territory": ["外部軸リスト"],
                        "turbo_message": "熱いメッセージ",
                        "boost_action": "具体的な1mmの前進行動（趣味があればそれを活用、なければ五感ワーク）",
                        "somatic_work": "五感アプローチまたは身体調整"
                    }}
                    """
                    res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    st.session_state.brain_scan = json.loads(res.text)
                    st.session_state.external_occupancy = st.session_state.brain_scan.get('estimated_external_occupancy', 30)
                    move_to(3)
                except Exception as e: st.error(f"デバッグエラー: {e}")

# --- STEP 3: レポート ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 調律完了レポート")
    st.success(f"### 称号：『 {scan.get('daily_title', 'SUNAOな旅人')} 』")

    # 比率グラフ
    ext_p = st.session_state.external_occupancy
    r = 100 - ext_p
    fig, ax = plt.subplots(figsize=(6, 0.8))
    ax.barh(["Axis"], [r], color="#3498db")
    ax.barh(["Axis"], [ext_p], left=[r], color="#e67e22")
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}% / 🟠 外部軸: {ext_p}%")

    st.divider()
    st.subheader("🔍 デバッガーの見解")
    st.info(scan.get('audit_report', '...'))

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**🔵 あなたの領域 (70%)**")
        for t in scan.get('my_territory', []): st.write(f"✅ {t}")
    with col_r2:
        st.markdown("**🟠 外部の熱・燃料 (30%)**")
        for t in scan.get('external_territory', []): st.write(f"🔥 {t}")

    st.divider()
    st.subheader("🚀 70%エンジン・ブースト")
    st.markdown(f"**💬 Message:**\n> {scan.get('turbo_message', '...')}")
    st.warning(f"🔥 **今日の1mm更新アクション:** {scan.get('boost_action', '...')}")

    st.divider()
    st.subheader("🛠️ 身体スイッチ（Somatic Tuning）")
    st.write(scan.get('somatic_work', '...'))

    if st.button("機体をリセットして最初に戻る"): move_to(1)
