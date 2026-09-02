"""
YouTube Pro Video & Subtitle AI Studio (Luxury Modern SaaS Edition)
デザイン全面刷新版：
- 高級感のあるダークグラデーション＋グラスモフィズム風カードUI
- ステップ式ガイド（Step 1/2/3）で初心者が迷わないUX
- 3つの投入モード（動画直接・長文/SRT・1文クイック）
- 日本人が聞いて納得するネイティブ意訳＆YouTubeマーケ特化メタデータ生成
"""

import streamlit as st
import anthropic
import openai
import os
import tempfile

# ページ基本設定
st.set_page_config(
    page_title="TRANSLY PRO | YouTube海外展開 AIローカライズ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# モダンUIカスタムCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans JP', sans-serif;
    }
    
    /* 背景と全体トーン */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* メインヘッダーバナー */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 20px;
        padding: 36px 40px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(96, 165, 250, 0.4);
        color: #93C5FD;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        color: #FFFFFF;
    }
    .hero-desc {
        font-size: 0.95rem;
        color: #94A3B8;
        line-height: 1.6;
        margin: 0;
    }
    
    /* ステップカード案内 */
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 6px;
        background: #2563EB;
        color: white;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
    }
    .card-box {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* タブデザイン */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #EEF2F6;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 700;
        font-size: 0.9rem;
        color: #475569;
        background: transparent;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* ボタンのブラッシュアップ */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.65rem 1.5rem;
        font-size: 1rem;
        font-weight: 700;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.35);
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.45);
    }
    
    /* サイドバー */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# サイドバー設計（初心者用ガイド付き）
with st.sidebar:
    st.markdown("### ⚡ **API設定**")
    st.caption("※お持ちのAPIキーを入力してください。キーは安全に保護され、保持されません。")
    
    openai_key = st.text_input("🔑 OpenAI API Key (文字起こし・AI)", type="password", placeholder="sk-...")
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
    st.markdown("### 🌐 **ローカライズ詳細**")
    
    target_lang = st.selectbox(
        "翻訳先の言語",
        [
            "英語 (US - YouTubeスラング・日常会話)",
            "英語 (UK - イギリス日常会話)",
            "韓国語 (YouTube・WEBトゥーン風の自然な会話)",
            "繁体字中国語 (台湾・香港向け)",
            "簡体字中国語",
            "スペイン語",
            "フランス語"
        ]
    )
    
    channel_genre = st.selectbox(
        "動画のトーン＆世界観",
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

# プロンプト生成（日本人が納得する超自然なローカライズ）
def get_system_prompt(lang, genre, custom):
    return f"""あなたは世界トップレベルのYouTube専属ローカライズ・映像翻訳ディレクターです。

【最重要ミッション】
「直訳」を完全に排除してください。
直訳英語特有の硬さや不自然さをなくし、「ネイティブのYouTuberが普段のテンションで喋っている、あるいは日本人が聞いても違和感がない、生き生きとした感情表現」に意訳・ローカライズしてください。

【対象言語】: {lang}
【動画ジャンル】: {genre}
【個別ルール】: {custom if custom else "特になし"}

【翻訳方針】
1. **文脈優先の意訳**: 日本語独特の相槌（「えーと」「マジで」「あり得ないんだけど」）や感情のニュアンスを、ネイティブが直感的に笑える・共感できるスラングや慣用表現に変換してください。
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

# メインヘッダー
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">YouTube Creator Suite PRO</div>
    <div class="hero-title">YouTube Pro 映像ローカライズ Studio</div>
    <div class="hero-desc">直訳ゼロ！動画・台本・フレーズを入れるだけで、ネイティブが普段使う自然な日常会話・スラングへ完全意訳。<br>タイトル・概要欄・サムネイル英文まで一括生成し、海外展開を最短化します。</div>
</div>
""", unsafe_allow_html=True)

# 3つの投入モードタブ
tab1, tab2, tab3 = st.tabs([
    "🎥 モード1: 動画・音声を直接投入（全自動）",
    "📋 モード2: 台本・SRTコピペ翻訳",
    "✍️ モード3: 1文クイック翻訳（テロップ/サムネ）"
])

# ----------------- モード1 -----------------
with tab1:
    st.markdown("""
    <div class="card-box">
        <span class="step-badge">1</span><strong>動画または音声ファイルをアップロード</strong>
        <p style="font-size:0.88rem; color:#64748B; margin: 4px 0 16px 0;">MP4 / MOV / MP3 などを入れるだけで、音声認識からローカライズ字幕・運用メタデータまで一瞬で完了します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    media_file = st.file_uploader("動画・音声ファイルを選択またはドロップ", type=["mp4", "mov", "mp3", "wav", "m4a"], key="u_media")
    
    col_opt1, _ = st.columns([1, 1])
    with col_opt1:
        gen_meta_video = st.checkbox("🎯 海外向けタイトル3案・概要欄・サムネ用コピーも同時生成する", value=True)
        
    btn_video = st.button("⚡ 動画から全自動でローカライズ字幕を一括生成", type="primary", key="btn_v")
    
    if btn_video:
        if not openai_key:
            st.error("⚠️ 音声認識のため、左側サイドバーに「OpenAI API Key」を入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ 左側サイドバーに「Anthropic API Key」を入力してください。")
        elif not media_file:
            st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
        else:
            with st.status("🎬 全自動ローカライズ処理を実行中...", expanded=True) as status:
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
        <span class="step-badge">2</span><strong>台本テキストまたは既存SRT字幕を貼り付け</strong>
        <p style="font-size:0.88rem; color:#64748B; margin: 4px 0 16px 0;">長文のストーリーやテロップ台本をコピペするだけで、文脈を考慮した違和感のない翻訳へ変換します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    text_input_type = st.radio("入力するデータの種類", ["日本語の台本テキスト（通常の文章）", "SRT字幕ファイル（タイムコード付きデータ）"], horizontal=True)
    raw_text = st.text_area("ここに台本またはSRT字幕をペースト", height=180, placeholder="テキストを貼り付けてください...")
    
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
            with st.spinner("文脈とニュアンスを分析し、自然な表現に翻訳中..."):
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
        <span class="step-badge">3</span><strong>1文クイック翻訳（テロップ・サムネイル用インパクト文字）</strong>
        <p style="font-size:0.88rem; color:#64748B; margin: 4px 0 16px 0;">「これって英語でどう言えば一番伝わる？」を1発解決。スラング・サムネ煽り・日常会話の3パターンを同時提案します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    single_phrase = st.text_input("翻訳したいフレーズを入力", placeholder="例: マジで許せないんだけど、これどう思う？ / 衝撃の結末を見逃すな")
    btn_single = st.button("🔍 複数の表現・スラングを提案", type="primary", key="btn_s")
    
    if btn_single:
        if not single_phrase.strip():
            st.warning("⚠️ フレーズを入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ 左側サイドバーに「Anthropic API Key」を入力してください。")
        elif "GPT-4o" in engine and not openai_key:
            st.error("⚠️ 左側サイドバーに「OpenAI API Key」を入力してください。")
        else:
            with st.spinner("ネイティブが使う複数のパターンを生成中..."):
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
