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

# APIキーの設定
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # 最新モデルを指定（環境に合わせて調整してください）
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
        st.caption("理想、やりたいこと、身体感覚。")
        st.session_state.sunao_input = st.text_area("今の本音（空欄OK）", height=150, key="sunao_t", placeholder="例：英語をマスターしたい。筋トレして強くなりたい。")
    with col_in2:
        st.markdown("### 🟠 外部軸 (External-Axis)")
        st.caption("他人の目、未練、期待、不安。")
        st.session_state.social_input = st.text_area("外部の重み（空欄OK）", height=150, key="social_t", placeholder="例：あの時こうしていれば。周りに褒められたい。")

    st.divider()

    st.subheader("🧠 外部軸の脳内占有率")
    ext_percent = st.slider("占有率を選択 (10%刻み)", min_value=0, max_value=100, value=30, step=10, key="ext_p")
    st.session_state.external_occupancy = ext_percent

    # プログレスバーの表示
    r = int(52 + (231 - 52) * (ext_percent / 100))
    g = int(152 + (76 - 152) * (ext_percent / 100))
    b = int(219 + (60 - 219) * (ext_percent / 100))
    bar_color = f"rgb({r}, {g}, {b})"

    st.markdown(f"""
        <div style="width: 100%; background-color: #eee; border-radius: 10px; overflow: hidden; height: 24px; border: 1px solid #ddd;">
            <div style="width: {ext_percent}%; background-color: {bar_color}; height: 100%; transition: width 0.4s ease-out;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.session_state.small_lights = st.text_input("🕯️ 今日の「ささいな光」（空欄OK）")

    if st.button("AIによる全統合デバッグを実行 ➔", type="primary"):
        with st.spinner("心のノイズを冷却中..."):
            try:
                model = genai.GenerativeModel(model_id)
                # --- プロンプトに「仕分け」と「ターボ」の指示を追加 ---
                prompt = f"""
                あなたは、ユーザーの心と体に寄り添い、全盛期を引き出すデバッガーです。
                ユーザーの入力を「自分軸(70%)」と「外部軸(30%)」に再構成してください。

                【データ】
                自分軸: {st.session_state.sunao_input}
                外部軸: {st.session_state.social_input}
                占有率: {st.session_state.external_occupancy}%
                
                【必須タスク】
                1. 境界線デバッグ(仕分け): 入力内容を「自分の課題(70%)」と「他人の課題(30%)」に明確に分離して。
                2. ターボチャージャー(変換): 外部軸にある不安や未練（排気）を、今日一歩進むための具体的な「ブースト行動（吸気）」に変換して。
                
                【JSON構造】
                {{
                    "daily_title": "称号",
                    "judged_self_ratio": {100 - st.session_state.external_occupancy},
                    "ratio_analysis": "現在のバランス解説",
                    "my_tasks": ["自分の領土にある課題のリスト"],
                    "others_tasks": ["他人の領土（手放すべき）課題のリスト"],
                    "turbo_boost": "外部軸の熱を力に変える具体的な一歩",
                    "somatic_work": "身体へのアプローチ"
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"解析エラー: {e}")

# --- STEP 3: レポート (仕分け & ターボ) ---
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

    # --- 機能1: 境界線デバッガー (仕分け) ---
    st.subheader("⚖️ 境界線デバッガー（仕分け）")
    st.markdown("「自分でコントロールできること」だけに集中しましょう。")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("**🔵 自分の課題 (70%)**")
        for task in scan.get('my_tasks', []):
            st.write(f"- {task}")
    with s_col2:
        st.markdown("**🟠 他人の課題 (30%)**")
        for task in scan.get('others_tasks', []):
            st.write(f"- {task}")
            
    st.divider()

    # --- 機能2: 30% ターボチャージャー (変換) ---
    st.subheader("🚀 30% ターボチャージャー（変換）")
    st.info(f"**【排気を吸気に変換完了】**\n外部への想いや不安を、今日のブーストに変えます。")
    st.warning(f"🔥 **ブースト行動:** {scan.get('turbo_boost', '...')}")

    st.divider()
    st.write(f"🛠️ **身体スイッチ:** {scan.get('somatic_work', '...')}")

    if st.button("最初に戻る"): move_to(1)
