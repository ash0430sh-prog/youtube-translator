"""
TRANSLY PRO | AI Hologram Core Edition
- 提示されたホログラムAIロボットの世界観を完全再現
- サイバー・データベース空間でホログラムロボットがパルス発光しながら浮遊するアニメーション
- 高度なネオンシアン（#00F2FE）アクセント ＆ グラスモーフィズムUI
- 視認性を極限まで高めたUI・ボタン・タブ
"""

import streamlit as st
import anthropic
import openai
import os
import tempfile

st.set_page_config(
    page_title="TRANSLY PRO | AI Hologram Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Noto+Sans+JP:wght@500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    /* 深層サイバーラボ背景 */
    .stApp {
        background-color: #050811;
        background-image: 
            radial-gradient(circle at 85% 15%, rgba(0, 242, 254, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 15% 85%, rgba(79, 172, 254, 0.1) 0%, transparent 45%),
            linear-gradient(rgba(5, 8, 17, 0.92), rgba(8, 14, 28, 0.96)),
            url('https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=2670&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #E2E8F0;
    }
    
    /* サイドバー高視認性デザイン */
    [data-testid="stSidebar"] {
        background: rgba(6, 11, 24, 0.96) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
        box-shadow: 10px 0 25px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
    }
    [data-testid="stSidebar"] .stCaption {
        color: #7DD3FC !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00F2FE !important;
        letter-spacing: 0.08em;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
    }

    /* メインヘッダーカード */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(13, 22, 44, 0.8) 0%, rgba(8, 15, 30, 0.9) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 242, 254, 0.35);
        border-radius: 22px;
        padding: 34px 44px;
        margin-bottom: 24px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }
    
    /* ホログラム投影ロボットアニメーション */
    .holo-wrapper {
        position: absolute;
        right: 35px;
        top: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        pointer-events: none;
    }
    .holo-cube {
        width: 100px;
        height: 100px;
        position: relative;
        border: 2px solid rgba(0, 242, 254, 0.6);
        border-radius: 12px;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 20px rgba(0, 242, 254, 0.2);
        animation: holoFloat 3.8s ease-in-out infinite alternate;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 242, 254, 0.04);
    }
    .holo-eyes {
        font-size: 2.8rem;
        filter: drop-shadow(0 0 12px #00F2FE);
        animation: pulseEye 2s infinite;
    }
    .holo-base {
        width: 120px;
        height: 14px;
        background: linear-gradient(90deg, #64748B, #CBD5E1, #64748B);
        border-radius: 4px;
        margin-top: 10px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.5);
    }
    
    @keyframes holoFloat {
        0% { transform: translateY(0px) scale(1); }
        100% { transform: translateY(-10px) scale(1.02); }
    }
    @keyframes pulseEye {
        0%, 100% { opacity: 0.85; filter: drop-shadow(0 0 8px #00F2FE); }
        50% { opacity: 1; filter: drop-shadow(0 0 18px #38BDF8); }
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'Orbitron', sans-serif;
        background: rgba(0, 242, 254, 0.12);
        border: 1px solid rgba(0, 242, 254, 0.45);
        color: #38BDF8;
        font-size: 0.8rem;
        font-weight: 800;
        padding: 5px 15px;
        border-radius: 9999px;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.25);
    }
    .hero-title {
        font-family: 'Orbitron', 'Noto Sans JP', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0 0 8px 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #BAE6FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-desc {
        font-size: 0.94rem;
        color: #94A3B8;
        line-height: 1.6;
        margin: 0;
        max-width: 78%;
    }
    
    /* タブデザイン（極太・近未来発光） */
    .stTabs [data-baseweb="tab-list"] {
        gap: 14px;
        background-color: rgba(10, 18, 38, 0.7);
        backdrop-filter: blur(12px);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(0, 242, 254, 0.25);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 900 !important;
        font-size: 0.98rem !important;
        letter-spacing: 0.04em;
        color: #64748B;
        background: transparent;
        border: none !important;
        transition: all 0.25s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #050811 !important;
        font-weight: 900 !important;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.55) !important;
    }

    /* ステップバッジ */
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }
    .step-pill {
        font-family: 'Orbitron', sans-serif;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 4px 14px;
        border-radius: 20px;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        color: #050811;
        font-size: 0.82rem;
        font-weight: 900;
        letter-spacing: 0.05em;
        white-space: nowrap;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
    }
    .step-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    
    .card-box {
        background: rgba(13, 22, 44, 0.65);
        backdrop-filter: blur(14px);
        border-radius: 16px;
        padding: 22px;
        border: 1px solid rgba(0, 242, 254, 0.18);
        margin-bottom: 20px;
    }

    /* 実行ボタン（ホログラム・ネオンシアン） */
    div.stButton > button:first-child {
        font-family: 'Orbitron', 'Noto Sans JP', sans-serif;
        background: linear-gradient(135deg, #00F2FE 0%, #0072FF 100%);
        color: #050811;
        border-radius: 12px;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.05rem;
        font-weight: 900 !important;
        letter-spacing: 0.04em;
        box-shadow: 0 4px 25px rgba(0, 242, 254, 0.45);
        transition: all 0.25s ease;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 35px rgba(0, 242, 254, 0.65);
        filter: brightness(1.08);
    }
</style>
""", unsafe_allow_html=True)

# サイドバー設計
with st.sidebar:
    st.markdown("### ⚡ SYSTEM & KEYS")
    st.caption("🔒 キーはお客様のブラウザ内でのみ安全に利用され、外部に保存されません。")
    
    openai_key = st.text_input("🔑 OpenAI API Key (音声文字起こし・AI)", type="password", placeholder="sk-...")
    engine = st.selectbox(
        "🧠 翻訳AIモデル",
        ["Claude 3.5 Sonnet (推奨：圧倒的に自然な意訳)", "GPT-4o (OpenAI)"]
    )
    
    if "Claude" in engine:
        claude_key = st.text_input("🔑 Anthropic API Key (翻訳用)", type="password", placeholder="sk-ant-...")
        model_name = "claude-3-5-sonnet-20241022"
    else:
        claude_key = ""
        model_name = "gpt-4o"
        
    st.divider()
    st.markdown("### 🌐 LOCALIZE CORE")
    
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "英語 (US - YouTube日常会話・スラング)",
            "英語 (UK - イギリス口語会話)",
            "韓国語 (YouTube・WEBトゥーン風の自然な会話)",
            "繁体字中国語 (台湾・香港向け)",
            "簡体字中国語",
            "スペイン語",
            "フランス語"
        ]
    )
    
    channel_genre = st.selectbox(
        "動画ジャンル・世界観",
        [
            "🔥 YouTubeエンタメ・実況（テンポ重視・スラング適応）",
            "📖 2ch/修羅場/スカッと系（口語・感情爆発・テンポ良い煽り）",
            "👻 ホラー・怪談・ミステリー（情緒的・不穏・引き込まれる語り）",
            "💡 ビジネス・解説・教養（分かりやすく知的な口調）",
            "⚡ ショート/リール/TikTok（超短縮・インパクト重視）"
        ]
    )
    
    custom_rule = st.text_area(
        "個別ルール・固有名詞（任意）",
        placeholder="例: 主人公の『イッチ』はフランクに。専門用語『○○』は訳さずそのままアルファベット表記にして。"
    )

def get_system_prompt(lang, genre, custom):
    return f"""あなたは世界トップレベルのYouTube専属ローカライズ・映像翻訳ディレクターです。

【最重要ミッション】
「直訳」を完全に排除してください。
直訳英語特有の硬さや不自然さをなくし、「ネイティブのYouTuberが普段のテンションで喋っている、あるいは日本人が聞いても違和感がない、生き生きとした感情表現」に意訳・ローカライズしてください。

【対象言語】: {lang}
【動画ジャンル】: {genre}
【個別ルール】: {custom if custom else "特になし"}

【翻訳方針】
1. **文脈優先の意訳**: 日本語独特の相槌や感情のニュアンスを、ネイティブが直感的に笑える・共感できるスラングや慣用表現に変換してください。
2. **文字数・テンポの配慮**: 動画内で視聴者が0.5秒〜1秒で読めるよう、無駄に長い文構造を避け、パンチのある言葉を選んでください。
3. **字幕形式の保護**: SRTデータの場合、番号とタイムコード（00:00:00,000 --> 00:00:00,000）は絶対に1文字も崩さず、テキスト部分のみを入れ替えてください。
"""

def call_ai(prompt, user_content, engine_choice, o_key, c_key, m_name):
    if "Claude" in engine_choice:
        client = anthropic.Anthropic(api_key=c_key)
        res = client.messages.create(
            model=m_name,
            max_tokens=4096,
            system=prompt,
            messages=[{"role": "user", "content": user_content}],
            temperature=0.3
        )
        return res.content[0].text
    else:
        client = openai.OpenAI(api_key=o_key)
        res = client.chat.completions.create(
            model=m_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3
        )
        return res.choices[0].message.content

def transcribe_media(file_bytes, file_ext, key):
    client = openai.OpenAI(api_key=key)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as audio_file:
            srt = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt"
            )
        return srt
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# メインヘッダー（ホログラムロボット投影UI）
st.markdown("""
<div class="hero-container">
    <div class="holo-wrapper">
        <div class="holo-cube">
            <div class="holo-eyes">👀</div>
        </div>
        <div class="holo-base"></div>
    </div>
    <div class="hero-badge">⚡ CYBERNETIC AI CORE</div>
    <div class="hero-title">TRANSLY PRO 映像ローカライズ</div>
    <div class="hero-desc">直訳を完全排除。ネイティブYouTubeスラングや自然な口語表現に完全意訳。<br>動画から直接字幕SRT・海外向けタイトル3選・概要欄・サムネ用英文まで一撃生成します。</div>
</div>
""", unsafe_allow_html=True)

# 3つの投入モードタブ
tab1, tab2, tab3 = st.tabs([
    "🎬 【MODE 1】 動画・音声を直接投入（全自動）",
    "📋 【MODE 2】 台本・SRT字幕コピペ翻訳",
    "⚡ 【MODE 3】 1文クイック提案（テロップ/サムネ）"
])

# ----------------- モード1 -----------------
with tab1:
    st.markdown("""
    <div class="card-box">
        <div class="step-header">
            <span class="step-pill">STEP 1</span>
            <span class="step-title">動画または音声ファイルをアップロード</span>
        </div>
        <p style="font-size:0.88rem; color:#94A3B8; margin: 4px 0 0 0;">MP4 / MOV / MP3 などを入れるだけで、音声認識からローカライズ字幕・運用メタデータまで一括出力します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    media_file = st.file_uploader("動画・音声ファイルをドロップ", type=["mp4", "mov", "mp3", "wav", "m4a"], key="u_media")
    
    col_opt1, _ = st.columns([1, 1])
    with col_opt1:
        gen_meta_video = st.checkbox("🎯 海外向けタイトル3案・概要欄・サムネ用コピーも同時生成する", value=True)
        
    btn_video = st.button("⚡ ホログラムAIで動画を自動解析・翻訳開始", type="primary", key="btn_v")
    
    if btn_video:
        if not openai_key:
            st.error("⚠️ 音声認識のため、左側サイドバーに「OpenAI API Key」を入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ 左側サイドバーに「Anthropic API Key」を入力してください。")
        elif not media_file:
            st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
        else:
            with st.status("🤖 ホログラムAIが動画ストリームを高速処理中...", expanded=True) as status:
                st.write("🎙️ 1/3 Whisperによる音声の自動文字起こし中...")
                _, ext = os.path.splitext(media_file.name)
                raw_srt = transcribe_media(media_file.getvalue(), ext, openai_key)
                
                st.write("🌐 2/3 ネイティブが使う自然な口調へ文脈意訳中...")
                sys_p = get_system_prompt(target_lang, channel_genre, custom_rule)
                translated_srt = call_ai(
                    sys_p,
                    f"以下のSRT字幕のタイムコードを完全に維持し、直訳を避けて最も自然なネイティブ表現に翻訳してください:\n\n{raw_srt}",
                    engine, openai_key, claude_key, model_name
                )
                
                meta_result = ""
                if gen_meta_video:
                    st.write("📈 3/3 海外YouTube向けタイトル3案・概要欄・サムネ用コピーを同時作成中...")
                    meta_prompt = f"""以下の動画字幕内容から、{target_lang}のYouTube視聴者が思わずクリックしたくなるコンテンツを作成してください。
【必須出力項目】
1. **海外向けクリック率特化タイトル案（3パターン）**：煽りすぎず引きが強いもの
2. **サムネイル用英語キャッチコピー（2〜4単語の短いインパクト文字）**
3. **SEO最適化概要欄（タイムスタンプ想定や関連タグ含む）**
"""
                    meta_result = call_ai(
                        meta_prompt,
                        f"動画の内容:\n{translated_srt[:2000]}",
                        engine, openai_key, claude_key, model_name
                    )
                status.update(label="✨ すべてのローカライズ処理が完了しました！", state="complete", expanded=False)
                
            st.markdown("### 📥 生成されたデータ")
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown("##### 🌍 翻訳済み字幕 (SRT)")
                st.text_area("Translated SRT", value=translated_srt, height=260)
                st.download_button(
                    "💾 翻訳字幕をダウンロード (.srt)",
                    data=translated_srt,
                    file_name=f"translated_{media_file.name}.srt"
                )
            with col_res2:
                st.markdown("##### 🇯🇵 原文文字起こし (SRT)")
                st.text_area("Original SRT", value=raw_srt, height=260)
                st.download_button(
                    "📄 日本語字幕をダウンロード (.srt)",
                    data=raw_srt,
                    file_name=f"original_{media_file.name}.srt"
                )
                
            if meta_result:
                st.markdown("---")
                st.markdown("### 🎯 YouTube運用パッケージ（タイトル・サムネ文・概要欄）")
                st.text_area("YouTube Metadata Package", value=meta_result, height=220)

# ----------------- モード2 -----------------
with tab2:
    st.markdown("""
    <div class="card-box">
        <div class="step-header">
            <span class="step-pill">STEP 2</span>
            <span class="step-title">台本テキストまたは既存SRT字幕を貼り付け</span>
        </div>
        <p style="font-size:0.88rem; color:#94A3B8; margin: 4px 0 0 0;">長文ストーリーや台本を貼るだけで、前後の文脈を汲み取った違和感のない翻訳へ変換します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    text_input_type = st.radio("入力するデータの形式", ["日本語の台本テキスト（通常の文章）", "SRT字幕ファイル（タイムコード付き）"], horizontal=True)
    raw_text = st.text_area("台本またはSRT字幕をペースト", height=180, placeholder="テキストを貼り付けてください...")
    
    gen_meta_text = st.checkbox("この台本からYouTube用タイトル・サムネ案も同時作成する", value=False, key="chk_m2")
    btn_text = st.button("⚡ テキストをネイティブ意訳する", type="primary", key="btn_t")
    
    if btn_text:
        if not raw_text.strip():
            st.warning("⚠️ テキストを入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ 左側サイドバーに「Anthropic API Key」を入力してください。")
        elif "GPT-4o" in engine and not openai_key:
            st.error("⚠️ 左側サイドバーに「OpenAI API Key」を入力してください。")
        else:
            with st.spinner("🤖 ホログラムAIが文脈を高速解析中..."):
                sys_p = get_system_prompt(target_lang, channel_genre, custom_rule)
                if "SRT" in text_input_type:
                    u_prompt = f"以下のSRT字幕のタイムコードを1文字も崩さず、テキスト部分のみをネイティブ向けに自然に翻訳してください:\n\n{raw_text}"
                else:
                    u_prompt = f"以下の日本語台本を、直訳を避けてネイティブが自然に共感できる口調に翻訳してください:\n\n{raw_text}"
                result_text = call_ai(sys_p, u_prompt, engine, openai_key, claude_key, model_name)
                
                st.markdown("### 📥 翻訳結果")
                st.text_area("Translated Output", value=result_text, height=220)
                st.download_button(
                    "💾 翻訳テキストをダウンロード (.txt)",
                    data=result_text,
                    file_name="translated_script.txt"
                )
                
                if gen_meta_text:
                    meta_p = f"以下の翻訳台本から、クリックされる英語タイトル3案とサムネ用コピーを提案してください:\n\n{result_text[:2000]}"
                    meta_res = call_ai(meta_p, "タイトルとサムネ案を生成してください。", engine, openai_key, claude_key, model_name)
                    st.markdown("##### 🎯 タイトル ＆ サムネ用コピー案")
                    st.text_area("Metadata", value=meta_res, height=180)

# ----------------- モード3 -----------------
with tab3:
    st.markdown("""
    <div class="card-box">
        <div class="step-header">
            <span class="step-pill">STEP 3</span>
            <span class="step-title">1文クイック提案（テロップ・サムネイル用インパクト文字）</span>
        </div>
        <p style="font-size:0.88rem; color:#94A3B8; margin: 4px 0 0 0;">「これってネイティブなら何て言う？」を即座に解決。スラング・サムネ煽り・日常会話の3パターンを同時提案します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    single_phrase = st.text_input("翻訳したいフレーズを入力", placeholder="例: マジで許せないんだけど、これどう思う？ / 衝撃の結末を見逃すな")
    btn_single = st.button("⚡ 複数の表現・スラングを提案", type="primary", key="btn_s")
    
    if btn_single:
        if not single_phrase.strip():
            st.warning("⚠️ フレーズを入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ 左側サイドバーに「Anthropic API Key」を入力してください。")
        elif "GPT-4o" in engine and not openai_key:
            st.error("⚠️ 左側サイドバーに「OpenAI API Key」を入力してください。")
        else:
            with st.spinner("🤖 AIがネイティブのYouTubeスラングや言い回しを考案中..."):
                single_prompt = f"""あなたはYouTube動画のテロップ・サムネイル作成のプロです。
日本語フレーズ: 「{single_phrase}」
動画ジャンル: {channel_genre}
言語: {target_lang}

【指示】
直訳ではなく、海外のYouTubeやSNSで実際に使われる以下の4パターンの自然な言い回しを出力してください：
1. **YouTubeスラング・カジュアル（感情的・一番リアルな若者言葉）**
2. **サムネイル用（2〜3単語で目立つ超短縮インパクト表現）**
3. **ナチュラル標準（誰にでも通じる自然な日常会話）**
4. **解説（なぜこの表現になるのか、日本語とのニュアンスの違いを1行で）**
"""
                single_res = call_ai(single_prompt, "パターンの提案をお願いします。", engine, openai_key, claude_key, model_name)
                st.markdown("### 💡 提案結果")
                st.markdown(single_res)
