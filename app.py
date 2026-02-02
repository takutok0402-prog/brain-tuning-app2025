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
st.set_page_config(page_title="SUNAO | Somatic Resilience", page_icon="🧘", layout="centered")

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash'
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
if 'step' not in st.session_state: st.session_state.step = 1
if 'brain_scan' not in st.session_state: st.session_state.brain_scan = None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: 機体ステータス・スキャン（維持） ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 身体ステータス")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 睡眠", options=["寝てない", "少し", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ", options=["絶好調", "普通", "疲れてる", "ボロボロ"], value="普通")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ", options=["なし", "少し", "そこそこ", "ずっと"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 空腹", options=["満腹", "普通", "ちょいペコ", "ペコ"], value="普通")
    
    if st.button("Step 2 へ進む ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ（AI判定モード） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 軸の成分を書き出す")
    st.markdown("比率は後ほどAIが判定します。思うままに書き出してください。")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🔵 自分軸 (Self-Axis)")
        st.caption("自分に必要だと思うこと、自分の理想、成長したいところ。")
        st.session_state.sunao_input = st.text_area("今の本音・理想（空欄でもOK）", height=200, key="sunao_t")
    with col_in2:
        st.markdown("### 🟠 外部軸 (External-Axis)")
        st.caption("素直に他人に期待すること、義務感、責任感、プレッシャー。")
        st.session_state.social_input = st.text_area("外部からの声・期待・責任感", height=200, key="social_t")

    if st.button("AIによる調律を実行 ➔", type="primary"):
        with st.spinner("AIが比率を解析中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                【解析対象】
                - 自分軸の内容: {st.session_state.sunao_input}
                - 外部軸の内容: {st.session_state.social_input}
                - 機体状態: 睡眠={st.session_state.sleep_val}, 疲労={st.session_state.fatigue_val}

                【判定・調律ガイドライン】
                1. 軸の判定: 入力内容の熱量や具体性から、現在の比率（自分軸％：外部軸％）を客観的に判定してください。
                2. 30%の尊重: 外部軸を「邪魔なもの」として切り捨てるのではなく、自分軸を高く跳ばせるための「支点」や「反発力」としてその価値を肯定してください。
                3. 軸ブースト/探索: 自分軸が空欄なら「五感の快楽（音楽・映画）」を提案。入力があればそれを70%へ引き上げるアクションを提案。
                4. エサレン流身体スイッチ(1分)を提示。

                【JSON構造】
                {{
                    "judged_self_ratio": 70, 
                    "ratio_analysis": "AIによる比率判定の理由",
                    "axis_action": "自分軸を70%へ持っていくための具体的な提案",
                    "respect_external": "30%の外部軸が持つポジティブな意味の通訳",
                    "daily_title": "今日を生きるあなたの称号",
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

# --- STEP 3: 調律レポート ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 調律完了レポート")
    st.success(f"### あなたの称号：『 {scan['daily_title']} 』")
    
    # AI判定された比率のビジュアライズ
    fig, ax = plt.subplots(figsize=(6, 1.2))
    r = scan['judged_self_ratio']
    ax.barh(["Axis"], [r], color="#3498db")
    ax.barh(["Axis"], [100-r], left=[r], color="#e67e22")
    ax.set_xlim(0, 100)
    ax.axis('off')
    st.pyplot(fig)
    st.caption(f"🔵 自分軸: {r}% / 🟠 外部軸: {100-r}% (AIによる客観判定)")

    st.divider()
    st.info(f"⚖️ **比率のデバッグ分析:**\n{scan['ratio_analysis']}")
    st.success(f"🚀 **自分軸(70%)への道:**\n{scan['axis_action']}")
    st.warning(f"🤝 **30%の外部軸を尊重する:**\n{scan['respect_external']}")
    
    st.subheader("🛠️ 身体スイッチ")
    st.write(scan['somatic_work']['action'])
    if scan['somatic_work'].get('hearing_url'): st.video(scan['somatic_work']['hearing_url'])

    if st.button("最初に戻る"): move_to(1)
