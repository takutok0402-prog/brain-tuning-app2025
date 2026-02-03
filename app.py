import streamlit as st
import google.generativeai as genai
import os
import json
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- 0. 環境・フォント設定 ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Holistic Tuner", page_icon="🧘", layout="centered")

# APIキーの設定（Renderなどの環境変数、またはStreamlit Secretsから取得）
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション状態の管理
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 身体スキャン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 身体スキャン")
    st.markdown("『今の自分』というコンディションを確認します。")
    
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
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "爆発しそう"]
        st.session_state.energy_val = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務）の強さ", ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "最高"]
        st.session_state.pleasant_val = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")

    if st.button("Step 2 へ進む ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ & 占有率 ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 軸の成分と占有率")
    st.info("✨ **空欄があっても大丈夫です。**\n言葉にならない時は、そのまま次へ進んでください。")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 自分軸 (Self-Axis)")
        st.caption("理想、やりたいこと、成長。")
        st.session_state.sunao_input = st.text_area("今の本音（空欄OK）", height=150, key="sunao_t", placeholder="例：英語を習得したい。次の大会で勝ちたい。...")
    with col_in2:
        st.markdown("### 🟠 外部軸 (External-Axis)")
        st.caption("義務、プレッシャー、他人の目、外部期待。")
        st.session_state.social_input = st.text_area("外部の重み（空欄OK）", height=150, key="social_t", placeholder="例：誰かの視線、何かいいことないかな...")

    st.divider()

    # --- 脳内占有率：11段階グラデーションスライダー ---
    st.subheader("🧠 外部軸の脳内占有率")
    st.caption("その悩みや義務は、今脳内のどれくらいを占領してる？")
    
    ext_percent = st.slider("占有率を選択 (10%刻み)", min_value=0, max_value=100, value=30, step=10, key="ext_p")
    st.session_state.external_occupancy = ext_percent

    # 色の計算（青 #3498db (52,152,219) から 赤 #e74c3c (231,76,60) への補完）
    r = int(52 + (231 - 52) * (ext_percent / 100))
    g = int(152 + (76 - 152) * (ext_percent / 100))
    b = int(219 + (60 - 219) * (ext_percent / 100))
    bar_color = f"rgb({r}, {g}, {b})"

    # 動的なグラデーションバーとガイド
    st.markdown(f"""
        <div style="width: 100%; background-color: #eee; border-radius: 10px; overflow: hidden; height: 24px; border: 1px solid #ddd;">
            <div style="width: {ext_percent}%; background-color: {bar_color}; height: 100%; transition: width 0.4s ease-out;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 5px; color: #888;">
            <span>最強の青 (0%)</span>
            <span>黄金比 (30%)</span>
            <span>警告の赤 (100%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    if ext_percent >= 70: st.error(f"🚨 占有率 {ext_percent}%：オーバーヒート中。仕分けが必要です。")
    elif ext_percent > 30: st.warning(f"⚠️ 占有率 {ext_percent}%：ノイズ混入。30%以下を目指しましょう。")
    elif ext_percent == 30: st.success(f"⚖️ 占有率 {ext_percent}%：完璧な黄金比！理想的な状態です。")
    else: st.info(f"💎 占有率 {ext_percent}%：超・自分軸モード。爆速で進めます。")

    st.session_state.small_lights = st.text_input("🕯️ 今日の「ささいな光」（空欄OK）")

    if st.button("AIによる全統合デバッグを実行 ➔", type="primary"):
        with st.spinner("心のノイズを冷却中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                あなたは、ユーザーの心と体に優しく寄り添うパートナーです。
                今の状態を「自分軸（70%）」と「外部軸（30%）」のバランスに整えてください。

                【データ】
                1. 体調: 睡眠={st.session_state.sleep_val}, 疲れ={st.session_state.fatigue_val}
                2. 自分軸: {st.session_state.sunao_input}
                3. 外部軸: {st.session_state.social_input}
                4. 脳内占有率(外部軸割合): {st.session_state.external_occupancy}%
                5. 今日の光: {st.session_state.small_lights}

                【アドバイス方針】
                1. 占有率診断: {st.session_state.external_occupancy}%という数値を見て、どう『仕分け』すべきか優しく助言して。
                2. 外部軸(30%): 義務や圧を、高く跳ぶための「追い風」や「反発力」として肯定的に捉え直して。
                3. 自分軸(70%): 空欄なら、心をホッとさせる五感の過ごし方を3つ。
                4. 称号: 温かくてかっこいい名前を付けて。

                【JSON構造】
                {{
                    "judged_self_ratio": {100 - st.session_state.external_occupancy}, 
                    "ratio_analysis": "占有率に基づいた心のバランス解説",
                    "axis_action": "自分らしく過ごすためのアクション",
                    "respect_external": "外部軸を味方にする考え方",
                    "daily_title": "あなたに贈る称号",
                    "somatic_work": "簡単なリラックス法"
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"解析エラー: {e}")

# --- STEP 3: レポート ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了")
    
    st.success(f"### 称号：『 {scan.get('daily_title', 'SUNAOな旅人')} 』")
    
    # 比率ビジュアライズ
    fig, ax = plt.subplots(figsize=(6, 1.2))
    r = scan.get('judged_self_ratio', 70)
    ax.barh(["Axis"], [r], color="#3498db") # 自分軸
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22") # 外部軸
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}% / 🟠 外部軸: {100-r}% (AI Tune)")

    st.divider()
    st.info(f"⚖️ **心のデバッグ報告:**\n{scan.get('ratio_analysis', '...')}")
    st.success(f"🚀 **自分軸(70%)を輝かせる:**\n{scan.get('axis_action', '...')}")
    st.warning(f"🤝 **30%の外部軸を味方にする:**\n{scan.get('respect_external', '...')}")
    st.write(f"🛠️ **身体スイッチ:** {scan.get('somatic_work', '...')}")

    if st.button("最初に戻る"): move_to(1)
