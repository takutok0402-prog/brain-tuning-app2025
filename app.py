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

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash'
else:
    st.error("APIキーが設定されていません。")

if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 機体ステータス ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 身体スキャン")
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

# --- STEP 2: 脳内ログ & 今日の光 ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 軸の成分と光の記録")
    
    # ここに「空欄OK」のメッセージを追加
    st.info("✨ **空欄があっても大丈夫です。**\n言葉にならない時は、そのまま次へ進んでください。AIがあなたの『身体の快』を呼び戻す提案をします。")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 自分軸 (Self-Axis)")
        st.caption("自分に必要だと思うこと、理想、成長したいところ。")
        st.session_state.sunao_input = st.text_area("今の本音・理想（空欄OK）", height=200, key="sunao_t", placeholder="例：英語を習得したい...")
    with col_in2:
        st.markdown("### 🟠 外部軸 (External-Axis)")
        st.caption("素直に他人に期待すること、義務、責任、プレッシャー。")
        st.session_state.social_input = st.text_area("外部からの声・期待（空欄OK）", height=200, key="social_t", placeholder="例：期待に応えなきゃ。なんか良いことないかな...")

    st.divider()
    st.subheader("🕯️ 今日の「ささいな光」")
    st.caption("今日感じた小さな心地よさ。見つからなければ『なし』でも構いません。")
    st.session_state.small_lights = st.text_input("例：コーヒーの香り、空の眺めの良さ", placeholder="（空欄でもAIがフォローします）")

    if st.button("AIによる全統合デバッグを実行 ➔", type="primary"):
        with st.spinner("身体・軸・光のデータを解析中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                あなたは人間心理と身体感覚のデバッガーです。
                ユーザーの状態を「70:30（自分軸：外部軸）」の黄金比に調律してください。

                【解析対象データ】
                1. 身体コンディション: 睡眠={st.session_state.sleep_val}, 疲労={st.session_state.fatigue_val}, 空腹={st.session_state.hunger_val}
                2. 自分軸（70%側: 理想・必要・成長）: {st.session_state.sunao_input}
                3. 外部軸（30%側: 期待・義務・責任・圧）: {st.session_state.social_input}
                4. 内在データ（光）: {st.session_state.small_lights}

                【調律（チューニング）ロジック】
                1. 比率判定（State Analysis）:
                   入力の具体性と機体疲労をクロス解析し、現在の「自分軸：外部軸」の比率を客観的に判定せよ。

                2. 外部軸(30%)の尊重（Structural Tension）:
                   外部の期待や義務を排除すべきノイズではなく、自分という機体を支え、理想を現実へと繋ぎ止める「必要な鎮痛剤」「ブースト」として肯定的に定義せよ。その重みをどう活用すれば、自分軸がより鮮明になるかを説け。

                3. 自分軸（70%）の最適化:
                   - 【入力あり】: その理想を意識の70%まで引き上げ、外部の圧をエネルギーに変換するためのマインドセットを提示せよ。
                   - 【入力なし】: 脳のオーバーロードと判断。五感（音楽・映画・食事など）を「感性の再起動データ」として、日常で即実行できる具体的な案を3つ提案せよ。

                4. 称号（ID）:
                   「自分に集中している状態」を肯定する、知的で洗練された称号を付与せよ。

                【JSON構造】
                {{
                    "judged_self_ratio": 70, 
                    "ratio_analysis": "現在の比率判定とその背景にある因果関係の解析",
                    "axis_action": "自分軸を70%へ引き上げる、または再起動するための具体的アクション",
                    "respect_external": "30%の外部要因が、今のあなたにとって持つポジティブな意味",
                    "daily_title": "現在のシステム称号",
                    "somatic_work": "1分間で身体感覚を今ここへ戻すワーク"
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
    
    # 安全にデータを取り出すための .get() を使用
    title = scan.get('daily_title', 'SUNAOな旅人')
    st.success(f"### 称号：『 {title} 』")
    
    fig, ax = plt.subplots(figsize=(6, 1.2))
    r = scan.get('judged_self_ratio', 70)
    ax.barh(["Axis"], [r], color="#3498db")
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22")
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)

    st.divider()
    # キーを ratio_analysis に統一
    st.info(f"⚖️ **比率のデバッグ:**\n{scan.get('ratio_analysis', '解析中...')}")
    st.success(f"🚀 **自分軸(70%)への道:**\n{scan.get('axis_action', '自分を信じて進みましょう。')}")
    st.warning(f"🤝 **30%の外部軸を尊重する:**\n{scan.get('respect_external', '外部の力もあなたの支えです。')}")
    st.write(f"🛠️ **身体スイッチ:** {scan.get('somatic_work', '深呼吸をしましょう。')}")

    if st.button("最初に戻る"): move_to(1)



