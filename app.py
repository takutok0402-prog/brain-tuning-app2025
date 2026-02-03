import streamlit as st
import google.generativeai as genai
import os
import json
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- 0. 環境・フォント設定 ---
# グラフ等の日本語化対応（環境に応じて調整）
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Holistic Tuner", page_icon="🧘", layout="centered")

# APIキーの設定（Render環境変数、またはStreamlit Secrets）
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' # 最新の高速・高機能モデル
else:
    st.error("APIキーが設定されていません。")

# セッション状態の管理
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 身体スキャン (機体のコンディション) ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 身体スキャン")
    st.markdown("今の「機体（身体）」の状態を測定します。")
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["寝てない", "少しだけ", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "ボロボロ"], value="普通")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそこ", "ずっと触っちゃう"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 お腹の空き具合", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")

    st.divider()
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.safebase_val = st.radio("🏠 今、居る場所は落ち着く？", ["安心できる", "少し揺らいでいる", "孤立・戦闘態勢"], index=0)
        st.session_state.energy_val = st.select_slider("⚡ 活性レベル", options=["動けない", "動きづらい", "普通", "動ける", "爆発しそう"], value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務）の強さ", ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        st.session_state.pleasant_val = st.select_slider("🍃 快・不快", options=["つらい", "少し嫌", "普通", "良い", "最高"], value="普通")

    if st.button("Step 2 へ進む ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ & 占有率 (70:30の仕分け準備) ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 軸の成分と占有率")
    st.info("✨ **未練、後悔、期待、不安。** すべてが燃料になります。")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 自分軸 (Self-Axis: 70%)")
        st.caption("本音、やりたいこと、身体感覚、理想。")
        st.session_state.sunao_input = st.text_area("今の本音（空欄OK）", height=150, placeholder="例：英語を取得したい。筋トレで強くなるんだ。")
    with col_in2:
        st.markdown("### 🟠 外部軸 (External-Axis: 30%)")
        st.caption("未練、後悔、他人の視線、執着、義務、不安。")
        st.session_state.social_input = st.text_area("外部の熱・ノイズ（空欄OK）", height=150, placeholder="例：あの時こうしてれば。期待に応えなきゃ。うまくいくかな、、")

    st.divider()

    st.subheader("🧠 外部軸（熱・ノイズ）の脳内占有率")
    ext_percent = st.slider("占有率を選択 (10%刻み)", min_value=0, max_value=100, value=30, step=10)
    st.session_state.external_occupancy = ext_percent

    # ビジュアル：青から赤へのグラデーション
    r = int(52 + (231 - 52) * (ext_percent / 100))
    g = int(152 + (76 - 152) * (ext_percent / 100))
    b = int(219 + (60 - 219) * (ext_percent / 100))
    st.markdown(f"""<div style="width: 100%; background-color: #eee; border-radius: 10px; height: 20px;"><div style="width: {ext_percent}%; background-color: rgb({r},{g},{b}); height: 100%; border-radius: 10px; transition: 0.5s;"></div></div>""", unsafe_allow_html=True)
    
    st.session_state.small_lights = st.text_input("🕯️ 今日の「ささいな光」（空欄OK）")

    if st.button("全エネルギーを動力に変換 ➔", type="primary"):
        with st.spinner("外部の熱を吸気エネルギーに変換中..."):
            try:
                model = genai.GenerativeModel(model_id)
                # --- 70:30理論 & 2階層アプローチのコア・プロンプト ---
                prompt = f"""
                あなたは「SUNAOシステム」のコアAIです。以下の理論に基づき、ユーザーの機体を調律してください。

                【70:30理論の設計思想】
                1. 境界線デバッグ(仕分け): 「自分の課題(70%)」と「他人の領土・過去(30%)」を厳格に分離。
                2. ターボチャージャー(変換): 不安や未練を否定せず、「30%の良質な燃料」として全肯定し、動力に変える。「消せ」ではなく「燃やせ」と伝える。
                3. 二階層アプローチ: 
                   - 自分軸が希薄な場合: 『グラウンディング・モード』として五感への介入を優先。
                   - 自分軸がある場合: 『アクセラレーション・モード』として外部の熱をターボ変換。

                【入力データ】
                自分軸: {st.session_state.sunao_input}
                外部軸: {st.session_state.social_input}
                占有率: {st.session_state.external_occupancy}%
                体調データ: 睡眠={st.session_state.sleep_val}, 疲れ={st.session_state.fatigue_val}, 活力={st.session_state.energy_val}
                
                【JSON構造】
                {{
                    "daily_title": "称号",
                    "judged_self_ratio": {100 - st.session_state.external_occupancy},
                    "mode": "Grounding or Acceleration",
                    "ratio_analysis": "現在のエネルギーバランスの客観的デバッグ結果",
                    "my_territory": ["自分の領土(70%)にある具体的課題"],
                    "external_territory": ["他人の領土・過去(30%)にある手放すべき事象"],
                    "turbo_message": "外部の熱を燃料として肯定し、背中を押す熱いメッセージ",
                    "boost_action": "今日すぐ実行できる、自分を前進させる一歩",
                    "somatic_work": "五感アプローチまたは身体調整法"
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"変換エラー: {e}")

# --- STEP 3: レポート (調律完了・ターボ起動) ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了")
    
    st.success(f"### 称号：『 {scan.get('daily_title', 'SUNAOな旅人')} 』")
    st.caption(f"モード: **{scan.get('mode', 'Unknown')}**")
    
    # 比率ビジュアライズ (matplotlib)
    fig, ax = plt.subplots(figsize=(6, 1))
    r = scan.get('judged_self_ratio', 70)
    ax.barh(["Axis"], [r], color="#3498db") # 自分軸
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22") # 外部軸
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}%（主体） / 🟠 外部軸: {100-r}%（燃料）")

    st.divider()

    # --- 機能1: 境界線デバッガー (仕分け) ---
    st.subheader("⚖️ 境界線デバッガー（仕分け）")
    st.markdown("「他人の領土」から意識を撤退させ、自分の聖域へリソースを回収します。")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("**🔵 自分の課題 (70%)**")
        for task in scan.get('my_territory', []): st.write(f"- {task}")
    with s_col2:
        st.markdown("**🟠 他人の領土・過去 (30%)**")
        for task in scan.get('external_territory', []): st.write(f"- {task}")
            
    st.divider()

    # --- 機能2: 30% ターボチャージャー (変換) ---
    st.subheader("🚀 30% ターボチャージャー（変換）")
    st.markdown(f"### 💬 Message\n> **{scan.get('turbo_message', '...')}**")
    
    st.info(f"**【排気を動力に変換済み】**\n未練や不安という「熱」を、自分を突き動かす『吸気エネルギー』に繋ぎ変えました。")
    st.warning(f"🔥 **今日のブースト行動:** {scan.get('boost_action', '...')}")

    st.divider()
    
    # --- 身体への落とし込み ---
    st.subheader("🛠️ 身体スイッチ")
    st.write(scan.get('somatic_work', '...'))

    st.markdown("---")
    if st.button("機体をリセットして最初に戻る"): move_to(1)
    
    # 哲学の刻印
    st.caption("70:30 Theory | 自律とは、外部を排除することではなく、スパイスとして使いこなすこと。")
