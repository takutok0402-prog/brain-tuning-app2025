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
    st.error("APIキーが未設定です。環境変数 GEMINI_API_KEY を確認してください。")

# セッション管理
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 身体スキャン（機体コンディション） ---
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
    st.session_state.safebase_val = st.radio("🏠 今、ここはあなたの「聖域（安心できる場所）」ですか？", ["はい", "いいえ（戦闘態勢/警戒中）"], index=0)

    if st.button("Step 2 脳内ログへ ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ & 占有率（仕分けの準備） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 軸の成分と占有率")
    st.info("✨ **心にあるものをすべて吐き出してください。** AIデバッガーがあなたの『領土』を正しく守ります。")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 あなたの領域 (Self-Axis)")
        st.caption("本音、やりたいこと、身体感覚、なりたい自分。")
        st.session_state.sunao_input = st.text_area("自分軸の箱", height=150, placeholder="例：英語を取得したい。筋トレで強くなるんだ。")
    with col_in2:
        st.markdown("### 🟠 社会の領域 (External-Axis)")
        st.caption("不安、後悔、他人の視線、執着、義務、未練。")
        st.session_state.social_input = st.text_area("外部軸（ノイズ・燃料）の箱", height=150, placeholder="例：あの時こうしてれば。期待に応えなきゃ。うまくいくかな、、")

    st.divider()
    st.subheader("🧠 外部軸が脳を占領している割合")
    ext_percent = st.slider("占有率を選択 (10%刻み)", 0, 100, 30, 10)
    st.session_state.external_occupancy = ext_percent

    # 占有率バーの視覚化
    r, g, b = (52 + (231 - 52) * (ext_percent / 100), 152 + (76 - 152) * (ext_percent / 100), 219 + (60 - 219) * (ext_percent / 100))
    st.markdown(f"""<div style="width: 100%; background-color: #eee; border-radius: 10px; height: 15px;"><div style="width: {ext_percent}%; background-color: rgb({int(r)},{int(g)},{int(b)}); height: 100%; border-radius: 10px;"></div></div>""", unsafe_allow_html=True)
    
    if st.button("全エネルギーを動力に変換 ➔", type="primary"):
        with st.spinner("デバッガーが領土を精査中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                あなたは「SUNAOシステム」の最強デバッガー兼メカニックです。

                【最重要任務：領土のオーディット（監査）】
                ユーザーが「自分軸」に書いた内容に、他人の反応や過去など「コントロール不能なこと」が混ざっていないか厳しく精査して。
                混ざっていたら、それを「外部軸」へ移動し、その理由をデバッガーとして優しく、論理的に説明して。

                【70:30理論の適用】
                1. 燃料肯定(Turbo): 外部軸の未練や不安を「素晴らしい熱量」として全肯定し、「燃やせ」と伝えて。
                2. 二階層調律(Somatic): 自分軸が希薄（空欄や混乱）なら「五感ワーク」、明確なら「加速ワーク」を処方して。

                【データ】
                自分軸: {st.session_state.sunao_input} / 外部軸: {st.session_state.social_input} / 占有率: {st.session_state.external_occupancy}%
                
                【JSON構造】
                {{
                    "daily_title": "称号",
                    "audit_report": "自分軸から外部軸へ移動させたものとその理由（無ければ『完璧な仕分け』と称賛）",
                    "my_territory": ["精査後の自分軸リスト"],
                    "external_territory": ["精査後の外部軸リスト"],
                    "turbo_message": "外部の熱を燃料として肯定し、背中を押す熱いメッセージ",
                    "boost_action": "今日すぐ実行できる、自分を前進させる具体的で小さな一歩",
                    "somatic_work": "五感アプローチまたは身体調整（自分軸の状態に合わせて選択）"
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"デバッグエラー: {e}")

# --- STEP 3: レポート（調律完了） ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 調律完了レポート")
    st.success(f"### 称号：『 {scan.get('daily_title', 'SUNAOな旅人')} 』")

    # 比率グラフ
    fig, ax = plt.subplots(figsize=(6, 0.8))
    r = 100 - st.session_state.external_occupancy
    ax.barh(["Axis"], [r], color="#3498db") # 自分軸
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22") # 外部軸
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}%（主体） / 🟠 外部軸: {100-r}%（燃料）")

    st.divider()
    st.subheader("🔍 デバッガーの領土オーディット")
    st.info(scan.get('audit_report', '...'))

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**🔵 守るべきあなたの聖域 (70%)**")
        for t in scan.get('my_territory', []): st.write(f"✅ {t}")
    with col_r2:
        st.markdown("**🟠 燃やすべき外部の熱 (30%)**")
        for t in scan.get('external_territory', []): st.write(f"🔥 {t}")

    st.divider()
    st.subheader("🚀 ターボチャージャー（変換）")
    st.markdown(f"**💬 Message:**\n> {scan.get('turbo_message', '...')}")
    st.warning(f"🔥 **今日のブースト行動:** {scan.get('boost_action', '...')}")

    st.divider()
    st.subheader("🛠️ 身体スイッチ（Somatic Tuning）")
    st.write(scan.get('somatic_work', '...'))

    if st.button("機体をリセットして最初に戻る"): move_to(1)

