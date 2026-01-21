import streamlit as st
import google.generativeai as genai
import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# --- 0. 環境対策 ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'IPAexGothic', 'DejaVu Sans']

# --- 1. システム設定 ---
st.set_page_config(page_title="SUNAO | Internal Conference", page_icon="🧘", layout="centered")

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
keys = ['step', 'brain_scan', 'selected_emotion', 'social_filter_val', 'fatigue_val', 'hunger_val', 
        'digital_val', 'safebase_val', 'sleep_val', 'meal_input', 'activity_input', 'sunao_input', 'social_input']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else "" if 'input' in key else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

def get_context():
    now_hour = datetime.datetime.now().hour
    is_night = 21 <= now_hour or now_hour <= 6
    return "夜間（前頭前野のブレーキが弱まり、扁桃体が過敏な時間）" if is_night else "日中"

# --- STEP 1: コンディション・スキャン (小池さん指定の構成を維持) ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 現在のステータス")
    st.markdown("身体のコンディションを教えてください")
    
    st.subheader("🔋 ハードウェア・ステータス")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["寝てない", "少しだけ", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "ボロボロ"], value="普通")
        st.session_state.meal_input = st.text_input("🥗 今日食べたもの", placeholder="例：ピザ、コンビニ、食べてない...")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそこ", "ずっと触っちゃう"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 お腹の空き具合", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")
        st.session_state.activity_input = st.text_input("🏃 今日の活動", placeholder="例：授業、仕事、何もしていない...")

    st.divider()
    
    st.subheader("🛡️ 心理的リソース")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.safebase_val = st.radio("🏠 今、居る場所は落ち着く？（安全基地）", 
                                              ["安心できる", "少し揺らいでいる", "孤立・戦闘態勢"], index=0)
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "爆発しそう"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務・プレッシャー）の強さ", 
                             ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "最高"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")

    e_idx, p_idx = energy_opts.index(energy) - 2, pleasant_opts.index(pleasant) - 2
    quad = "Red" if e_idx >= 0 and p_idx < 0 else "Yellow" if e_idx >= 0 and p_idx >= 0 else "Blue" if e_idx < 0 and p_idx < 0 else "Green"
    EM_DB = {
        "Red": ["嫌な事を考え続けてしまう", "不安", "心臓がバクバクする", "落ち着かない", "モヤモヤしている"],
        "Yellow": ["集中できている", "ワクワク", "自信がある", "挑戦したい"],
        "Blue": ["自分なんてダメだ", "布団から出られない", "消えてしまいたい", "どんより"],
        "Green": ["ほっとしている", "穏やか", "今のままでいい", "落ち着く"]
    }
    st.session_state.selected_emotion = st.selectbox(f"今の感覚に近いラベル（{quad}エリア）", ["(選択してください)"] + EM_DB[quad])

    if st.session_state.selected_emotion != "(選択してください)":
        if st.button("2.5 Flash でデバッグを開始 ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログの書き出し（「ささいな光」追加版） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内ログの書き出し")
    st.markdown("感情を吐き出せるだけどうぞ。単語でも空白でも大丈夫。")

    # 1. 葛藤の入力
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🟢 本音くん（願望）")
        st.caption("「〜したい」「戻りたい」という純粋な願望。")
        st.session_state.sunao_input = st.text_area("本当はどうしたい？", placeholder="例：あの頃に戻りたい。やりたくない。", height=200, key="sunao_t")
        
    with col_in2:
        st.markdown("### 🔴 義務さん（予定・現実）")
        st.caption("「〜しなきゃ」「今はこうだ」という現実。")
        st.session_state.social_input = st.text_area("〜しなきゃ、現実はこうだ", placeholder="例：前を向かなきゃ。自分がやらなきゃ。", height=200, key="social_t")

    st.divider()

    # 2. 新機能：ささいな光（Small Lights）
    st.markdown("### 🌟 今日の「ささいな光」")
    st.info("「しんどさが永遠に続く」という脳のバグを溶かすための、ささいなプラスを記録します。")
    st.session_state.small_lights = st.text_area(
        "今日、ほんの少しだけ心が動いたこと、良かったこと、親切にされたこと（解決とは無関係でOK）", 
        placeholder="例：車に道を譲ってもらった。コーヒーが美味しかった。BUMPの曲で少し元気が出た。",
        height=100
    )

    if st.button("調律プロセスを実行 ➔", type="primary"):
        with st.spinner("無意識の声を意識の部屋へエクスポート中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                【解析対象】
                - 願望（本音）: {st.session_state.sunao_input}
                - 現実/義務（予定）: {st.session_state.social_input}
                - ささいな光: {st.session_state.small_lights}
                - コンディション: 疲労={st.session_state.fatigue_val}, 安全基地={st.session_state.safebase_val}

                【2.5 Flash 調律ガイド】
                1. 「早く楽になりたい」「この苦しみは永遠だ」というユーザーが無意識に抱えるバイアスを優しく指摘し、それらを「誠実さの副産物」として定義し直してください。
                2. 「ささいな光」を、脳が新しい現実（安全な世界）を学習するための重要な反証データとして扱い、その出来事がユーザーのどんな誠実さに繋がっているか通訳してください。
                3. 解決を急がせず、「しんどいままでも、今日一日をクリアしたこと」を最大級に肯定してください。

                【JSON構造】
                {{
                    "sunao_claim": "本音くんの言い分",
                    "social_claim": "義務さんの言い分",
                    "deep_analysis": "ギャップと誠実さの分析",
                    "lifestyle_advice": ["提案1", "提案2"],
                    "light_translation": "「ささいな光」が持つ、今日をクリアした証としての意味",
                    "secure_msg": "安全基地からの言葉",
                    "daily_clear_label": "今日を生き延びた自分への二つ名（例：静かな開拓者、など）"
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"解析エラー: {e}")
    if st.button("← 戻る"): move_to(1)

# --- STEP 3: カンファレンス・レポート（光の通訳） ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 今日の調律完了")
    
    st.success(f"### 今日のあなたは：『 {scan['daily_clear_label']} 』")
    
    with st.expander("🕯️ 今日の「光」の通訳"):
        st.write(scan['light_translation'])
        st.caption("※ささいな幸せに気づけたことは、あなたの脳が『安全』を必死に探して、一歩前に進もうとしている誠実さの証拠です。")

    st.divider()
    
    col_out1, col_out2 = st.columns(2)
    with col_out1: st.info(f"🟢 **本音（願望）**\n\n「{scan['sunao_claim']}」")
    with col_out2: st.error(f"🔴 **義務（予定）**\n\n「{scan['social_claim']}」")
    
    st.subheader("🕵️ 調律師の視点")
    st.markdown(scan['deep_analysis'])
    
    st.subheader("🏠 安全基地からのメッセージ")
    st.write(scan['secure_msg'])
    
    if st.button("最初に戻る"): move_to(1)


# --- STEP 3: カンファレンス・レポート (矛盾の肯定) ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 脳内カンファレンス・ログ")
    
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        st.success(f"**🟢 本音くん（願望）**\n\n「{scan['sunao_claim']}」")
    with col_out2:
        st.error(f"**🔴 義務さん（予定・現実）**\n\n「{scan['social_claim']}」")
    
    st.divider()
    
    # 🕵️ 調律師の視点
    st.subheader("🕵️ 調律師の視点（意識の部屋）")
    st.info(scan['deep_analysis'])
    
    # ギャップの肯定
    with st.container():
        st.markdown("#### 💎 ギャップは誠実さの証")
        st.write(scan['gap_importance'])

    with st.expander("⚙️ ハードウェア・メンテナンス"):
        st.warning(scan['lifestyle_report'])
        for advice in scan['lifestyle_advice']:
            st.write(f"✅ {advice}")
    
    st.subheader("🕊️ 安全基地からのメッセージ")
    st.markdown(f"### {scan['secure_msg']}")
    st.write(scan['validation'])
    
    st.caption("※雨が降ってほしくないと思うことは自由です。その願いを抱えたまま、傘をさして一歩ずつ歩むあなたを、このシステムは全力で肯定します。")
    
    if st.button("最初に戻る"): move_to(1)

