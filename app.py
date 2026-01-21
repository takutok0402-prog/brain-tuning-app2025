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

# モデルIDを2.5 Flashに変更
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model_id = 'gemini-2.5-flash' 
else:
    st.error("APIキーが設定されていません。")

# セッション状態の初期化
keys = [
    'step', 'brain_scan', 'selected_emotion', 'social_filter_val', 'fatigue_val', 
    'hunger_val', 'digital_val', 'safebase_val', 'sleep_val', 'meal_input', 
    'activity_input', 'sunao_input', 'social_input', 'small_lights', 'moyomoyo_input'
]
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = 1 if key == 'step' else "" if 'input' in key or 'small' in key else None

def move_to(step):
    st.session_state.step = step
    st.rerun()

# --- STEP 1: コンディション・スキャン ---
if st.session_state.step == 1:
    st.title("🌈 Step 1: 現在のステータス")
    st.markdown("身体のコンディションを教えてください。めんどくさいとこは飛ばしても大丈夫。")
    
    st.subheader("🔋 ハードウェア・ステータス")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.session_state.sleep_val = st.select_slider("😴 昨夜の睡眠", options=["寝てない", "少しだけ", "そこそこ", "ぐっすり"], value="そこそこ")
        st.session_state.fatigue_val = st.select_slider("😫 疲れ・眠気", options=["絶好調", "普通", "ちょっと疲れてる", "ボロボロ"], value="普通")
    with v_col2:
        st.session_state.digital_val = st.select_slider("📱 スマホ利用", options=["なし", "少し", "そこそこ", "ずっと触っちゃう"], value="少し")
        st.session_state.hunger_val = st.select_slider("🍕 お腹の空き具合", options=["満腹", "普通", "ちょいペコ", "ペコペコ"], value="普通")

    st.divider()
    
    st.subheader("🛡️ 心理的リソース")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.safebase_val = st.radio("🏠 今、居る場所は落ち着く？", ["安心できる", "少し揺らいでいる", "孤立・戦闘態勢"], index=0)
        energy_opts = ["動けない", "動きづらい", "普通", "動ける", "爆発しそう"]
        energy = st.select_slider("⚡ 活性レベル", options=energy_opts, value="普通")
    with p_col2:
        st.session_state.social_filter_val = st.radio("⚖️ 社会性（義務）の強さ", ["全く気にならない", "少し気になる", "すごく気になる"], index=1)
        pleasant_opts = ["つらい", "少し嫌", "普通", "良い", "最高"]
        pleasant = st.select_slider("🍃 快・不快", options=pleasant_opts, value="普通")

    e_idx, p_idx = energy_opts.index(energy) - 2, pleasant_opts.index(pleasant) - 2
    quad = "Red" if e_idx >= 0 and p_idx < 0 else "Yellow" if e_idx >= 0 and p_idx >= 0 else "Blue" if e_idx < 0 and p_idx < 0 else "Green"
    EM_DB = {
        "Red": ["不安", "心臓がバクバクする", "落ち着かない", "モヤモヤ"],
        "Yellow": ["集中", "ワクワク", "自信", "挑戦"],
        "Blue": ["自分なんてダメだ", "布団から出られない", "消えてしまいたい"],
        "Green": ["ほっとしている", "穏やか", "今のままでいい"]
    }
    st.session_state.selected_emotion = st.selectbox(f"今の感覚に近いラベル（{quad}エリア）", ["(選択してください)"] + EM_DB[quad])

    if st.session_state.selected_emotion != "(選択してください)":
        if st.button("Step 2 へ進む ➔", type="primary"): move_to(2)

# --- STEP 2: 脳内ログ（ここを修正） ---
elif st.session_state.step == 2:
    st.title("🔍 Step 2: 脳内ログの書き出し")
    st.markdown("データは保存されません。個人情報にだけ気をつけて今の脳内をそのまま置いてください。単語でも空白でも大丈夫")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("### 🟢 本音くん（願望）")
        # 指定されたメッセージを反映
        st.info("💡 **ここがポイント**\n\n言いづらい、言葉にしづらいことこそ、大切な『本音』です。スラスラ出てこなくても大丈夫。「〜したい」「戻りたい」という純粋な**願望**をここに置いてください。")
        st.session_state.sunao_input = st.text_area("本当はどうしたい？", placeholder="（例：あの時こうしてれば。本当はやりたくない。）", height=250, key="sunao_t")
        
    with col_in2:
        st.markdown("### 🔴 義務さん（予定・現実）")
        st.caption("※社会性フィルターを通した『〜すべき』『〜しなきゃ』という声。")
        st.session_state.social_input = st.text_area("〜しなきゃ、現実はこうだ", placeholder="例：前を向かなきゃ。期待に応えなきゃ。", height=250, key="social_t")

    st.divider()

    col_in3, col_in4 = st.columns(2)
    with col_in3:
        st.markdown("### 🌟 今日の「ささいな光」")
        st.caption("記述することで「絶望の永続化」というバグを溶かします。")
        st.session_state.small_lights = st.text_area("良かったこと、親切にされたこと", placeholder="例：駅で道を譲ってもらった。コーヒーが美味しかった。", height=100)
    with col_in4:
        st.markdown("### ⚡ 今日の「モヤモヤ」")
        st.caption("自分の力では変えられない、イラッとしたこと。")
        st.session_state.moyomoyo_input = st.text_area("変えられない外部の事象", placeholder="例：前の車が遅い。雨が降った。", height=100)

    if st.button("調律プロセスを実行 ➔", type="primary"):
        with st.spinner("無意識の声を意識の部屋へエクスポート中..."):
            try:
                model = genai.GenerativeModel(model_id)
                prompt = f"""
                【解析対象】
                - 願望（本音）: {st.session_state.sunao_input}
                - 現実（義務）: {st.session_state.social_input}
                - ささいな光: {st.session_state.small_lights}
                - モヤモヤ: {st.session_state.moyomoyo_input}
                - コンディション: 疲労={st.session_state.fatigue_val}, 安全基地={st.session_state.safebase_val}

                【調律ガイド】
                1. 「早く楽になりたい」「この苦しみは永遠だ」というユーザーが無意識に抱えるバイアスを指摘し、それらを「誠実さの副産物」として定義し直してください。
                2. 「ささいな光」を、脳が安全を学習するための反証データとして通訳してください。
                3. 「モヤモヤ」に対し、相手の真実を当てるのではなく「自分を楽にするための優しい物語（仮説）」を3つ提案してください。
                4. 解決を急がせず、「しんどいまま、今日をクリアしたこと」を最大級に肯定してください。

                【JSON構造】
                {{
                    "sunao_claim": "本音くんの言い分",
                    "social_claim": "義務さんの言い分",
                    "deep_analysis": "矛盾と誠実さの深層分析",
                    "light_translation": "ささいな光が持つ意味の通訳",
                    "gentle_narratives": ["物語1", "物語2", "物語3"],
                    "secure_msg": "安全基地からの言葉",
                    "daily_clear_label": "今日を生き延びた自分への称号",
                    "lifestyle_report": "身体が脳に与えている影響",
                    "lifestyle_advice": ["具体的な提案1", "提案2"]
                }}
                """
                res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                st.session_state.brain_scan = json.loads(res.text)
                move_to(3)
            except Exception as e: st.error(f"解析エラー: {e}")
    if st.button("← 戻る"): move_to(1)

# --- STEP 3: カンファレンス・レポート ---
elif st.session_state.step == 3:
    scan = st.session_state.brain_scan
    st.title("📋 Step 3: 今日の調律完了")
    
    st.success(f"### 今日のあなたは：『 {scan['daily_clear_label']} 』")
    st.info(f"**🏠 安全基地より:** {scan['secure_msg']}")

    st.divider()
    
    with st.expander("🕯️ 今日の「光」の通訳"):
        st.write(scan['light_translation'])
    
    st.divider()

    st.subheader("🕵️ 「モヤモヤ」を書き換える優しい物語")
    for i, story in enumerate(scan['gentle_narratives']):
        if st.button(f"物語 {i+1} を採用してみる", key=f"story_{i}"):
            st.toast("物語を採用しました。脳の負荷が少し軽減されます。")
            st.balloons()
        st.write(f"> {story}")

    st.divider()

    col_out1, col_out2 = st.columns(2)
    with col_out1: st.info(f"🟢 **本音（願望）**\n\n「{scan['sunao_claim']}」")
    with col_out2: st.error(f"🔴 **義務（予定）**\n\n「{scan['social_claim']}」")
    
    st.markdown("#### 💎 葛藤の深層分析")
    st.write(scan['deep_analysis'])

    with st.expander("⚙️ ハードウェア・メンテナンス"):
        st.warning(scan['lifestyle_report'])
        for advice in scan['lifestyle_advice']:
            st.write(f"✅ {advice}")
    
    if st.button("最初に戻る"): move_to(1)
