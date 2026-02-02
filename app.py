import streamlit as st
import google.generativeai as genai
import os
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- 0. 環境設定 ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Somatic Tuner", page_icon="🧘", layout="centered")

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash'
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
keys = [
    'step', 'brain_scan', 'selected_emotion', 'social_filter_val', 'fatigue_val', 
    'hunger_val', 'digital_val', 'safebase_val', 'sleep_val', 'self_axis_ratio',
    'sunao_input', 'social_input', 'small_lights', 'moyomoyo_input'
]
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else 70 if key == 'self_axis_ratio' else ""

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: ハードウェア・ステータス（省略なし） ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 機体ステータス・スキャン")
    st.markdown("今の自分という『ハードウェア』の状態を確認します。")
    
    st.subheader("🔋 基本コンディション")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["寝てない", "少しだけ", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "ボロボロ"], value="普通")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそこ", "ずっと触っちゃう"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 お腹の空き具合", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")

    st.divider()
    st.subheader("🛡️ 心理的ベースライン")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.safebase_val = st.radio("🏠 今、居る場所は落ち着く？", ["安心できる", "少し揺らいでいる", "孤立・戦闘態勢"], index=0)
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "爆発しそう"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務）の強さ", ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "最高"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")

    if st.button("Step 2 へ進む ➔", type="primary"): move_to(2)

# --- STEP 2: 70:30 デバッグ・ログ（定義アップデート版） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 70:30 比率の調律")
    st.markdown("「自分に集中している自分、かっけー」の比率をデバッグします。")
    
    st.session_state.self_axis_ratio = st.slider("⚖️ 現在の自分軸の割合 (%)", 0, 100, 70)
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 自分軸 70%")
        st.caption("自分に必要だと思うこと、理想、成長したいこと。")
        st.session_state.sunao_input = st.text_area("今の本音・理想を教えて（空欄でもOK）", height=200, key="sunao_t")
    with col_in2:
        st.markdown("### 🟠 外部軸 30%")
        st.caption("他人に期待すること、義務感、責任感、プレッシャー。")
        st.session_state.social_input = st.text_area("押し込めておきたい期待や義務は？", height=200, key="social_t")

    st.divider()
    st.session_state.small_lights = st.text_input("🕯️ 今日の「ささいな光」")

    if st.button("調律プロセスを実行 ➔", type="primary"):
        with st.spinner("身体と脳の不整合をデバッグ中..."):
            try:
                model = genai.GenerativeModel(model_id)
                # 入力の有無によってモードを切り替えるプロンプト
                prompt = f"""
                【ユーザー状態】
                - 睡眠: {st.session_state.sleep_val}, 疲労: {st.session_state.fatigue_val}, 空腹: {st.session_state.hunger_val}
                - 自分軸(70%側 / 理想・成長): {st.session_state.sunao_input}
                - 外部軸(30%側 / 他人への期待・義務): {st.session_state.social_input}
                
                【解析・調律ミッション】
                1. 自分軸が「空欄」の場合:
                   - 脳が疲弊し、軸を見失っている状態と判断。
                   - 音楽、映画、食事など、五感を刺激して「身体の快」を取り戻すための具体的な案を3つ提案してください。
                
                2. 自分軸が「入力あり」の場合:
                   - その「理想」や「成長」を、意識の70%までブーストし、外部のノイズを30%以下に抑え込むための「全盛期マインドセット」を提案してください。

                3. 共通:
                   - 外部期待を30%フォルダに隔離するアドバイス。
                   - エサレン流の身体スイッチ(1分)を提示。

                【JSON構造】
                {{
                    "mode_status": "現在のモード（軸探索 or 軸ブースト）",
                    "axis_action": "具体的な行動提案（自分軸を70%にする、または見つけるためのアクション）",
                    "folder_technique": "30%フォルダへの隔離術",
                    "daily_title": "今日を生きるアスリートとしての称号",
                    "somatic_work": {{
                        "action": "1分間の身体ワーク内容",
                        "hearing_url": "https://www.youtube.com/watch?v=..."
                    }}
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"解析エラー: {e}")

# --- STEP 3: レポート（省略なし） ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了")
    st.success(f"### 称号：『 {scan['daily_title']} 』")
    
    # 比率グラフ
    fig, ax = plt.subplots(figsize=(6, 1.2))
    r = st.session_state.self_axis_ratio
    ax.barh(["Axis"], [r], color="#3498db")
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22")
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}% (理想) / 🟠 外部軸: {100-r}% (他者期待・義務)")

    st.divider()
    st.info(f"🚀 **{scan['mode_status']}:**\n{scan['axis_action']}")
    st.warning(f"📁 **30%フォルダ隔離術:** {scan['folder_technique']}")
    
    st.subheader("🛠️ 五感を起動する身体スイッチ")
    st.success(scan['somatic_work']['action'])
    if scan['somatic_work'].get('hearing_url'): st.video(scan['somatic_work']['hearing_url'])

    if st.button("最初に戻る"): move_to(1)
