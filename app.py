"""
YouTube Pro Video & Subtitle AI Studio (All-in-One Multi-Mode Edition)
- 3つの投入モード：
  1. 🎥 動画・音声ファイルから直接一括（自動文字起こし＋翻訳＋メタデータ）
  2. ✍️ 1文ずつのクイック入力（テロップ・サムネ文・煽り文句）
  3. 📋 長文テキスト / 台本コピペ（ブロック単位翻訳・SRT変換対応）
- 日本人が聞いて・読んで違和感のない「自然な日常表現」「スラング」「文脈最適化」に特化
- YouTube運営・動画編集者が欲しがる「クリック率特化タイトル案」「概要欄」「サムネキャッチコピー」同時出力
"""

import streamlit as st
import anthropic
import openai
import os
import tempfile

st.set_page_config(
    page_title="YouTube Pro Multi-Translation Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# スタイリング
st.markdown("""
<style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #F1F5F9;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
    }
    .output-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ システム・API設定")
    st.caption("※APIキーはお客様ご自身のキーを使用するため、運営者側に保持されず安全です。")
    
    openai_key = st.text_input("OpenAI API Key (動画文字起こし・AI用)", type="password", placeholder="sk-...")
    engine = st.selectbox("翻訳メインエンジン", ["Claude (Anthropic) - おすすめ：超自然な意訳", "ChatGPT (OpenAI GPT-4o)"])
    
    if "Claude" in engine:
        claude_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        model_name = "claude-3-5-sonnet-20241022"
    else:
        claude_key = ""
        model_name = "gpt-4o"
        
    st.divider()
    st.header("🌐 言語・トーン設定")
    
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "英語 (US - YouTubeネイティブの口語・日常会話)",
            "英語 (UK - イギリス日常会話)",
            "韓国語 (YouTube・WEBトゥーン風の自然な会話)",
            "繁体字中国語 (台湾・香港向け)",
            "簡体字中国語",
            "スペイン語",
            "フランス語"
        ]
    )
    
    channel_genre = st.selectbox(
        "動画ジャンル・チャンネルの空気感",
        [
            "🔥 YouTubeエンタメ・実況（テンポ重視・スラング・リアクション）",
            "📖 2ch/5ch風・修羅場・スカッと系（口語・感情爆発・テンポ良い煽り）",
            "👻 ホラー・怪談・ミステリー（情緒的・不穏・引き込まれる語り）",
            "💡 ビジネス・解説・教養（分かりやすく知的な口調）",
            "⚡ ショート/リール/TikTok（超短縮・インパクト最大化）"
        ]
    )
    
    custom_rule = st.text_area(
        "こだわり指示・固有名詞（任意）",
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

# AIリクエスト共通関数
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

# 音声文字起こし（Whisper）
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
st.markdown('<div class="main-title">🎬 YouTube Pro 映像・字幕ローカライズ Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">直訳ゼロ！ネイティブの日常会話やYouTubeスラングに完全意訳。編集者・運用者の海外展開を最短化します。</div>', unsafe_allow_html=True)

# 3つの投入モードタブ
tab1, tab2, tab3 = st.tabs([
    "🎥 モード1: 動画・音声を直接投入（全自動）",
    "📋 モード2: テキスト・台本コピペ（長文・SRT）",
    "✍️ モード3: 1文クイック翻訳（サムネ文・テロップ）"
])

# ----------------- モード1: 動画・音声投入 -----------------
with tab1:
    st.subheader("動画/音声ファイルをアップロード")
    st.caption("MP4, MOV, MP3等の動画や音声をそのまま入れるだけで、文字起こし＋自然な字幕＋YouTubeメタデータ（タイトル・概要欄・サムネ文）まで一括生成します。")
    
    media_file = st.file_uploader("ファイルをドラッグ＆ドロップ", type=["mp4", "mov", "mp3", "wav", "m4a"], key="media_uploader")
    col1, col2 = st.columns([1, 2])
    with col1:
        gen_meta_video = st.checkbox("YouTube用タイトル・概要欄・サムネ案も同時作成する", value=True)
        
    btn_video = st.button("🚀 動画から全自動でローカライズ生成", type="primary", key="btn_video")
    
    if btn_video:
        if not openai_key:
            st.error("⚠️ 音声認識のため、サイドバーに「OpenAI API Key」を入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ サイドバーに「Anthropic API Key」を入力してください。")
        elif not media_file:
            st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
        else:
            with st.status("🎬 処理中: 音声抽出・ネイティブ意訳・メタデータ生成...", expanded=True) as status:
                st.write("🎙️ 1/3 高精度文字起こしを実行中 (Whisper)...")
                _, ext = os.path.splitext(media_file.name)
                raw_srt = transcribe_media(media_file.getvalue(), ext, openai_key)
                
                st.write("🌐 2/3 日本語のニュアンスを崩さずネイティブ口調へ翻訳中...")
                sys_p = get_system_prompt(target_lang, channel_genre, custom_rule)
                translated_srt = call_ai(
                    sys_p,
                    f"以下のSRT字幕のタイムコードを完全に維持し、直訳を避けて最も自然なネイティブ表現に翻訳してください:\n\n{raw_srt}",
                    engine, openai_key, claude_key, model_name
                )
                
                meta_result = ""
                if gen_meta_video:
                    st.write("📈 3/3 海外YouTube向けタイトル3案・概要欄・サムネコピーを考案中...")
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
                
                status.update(label="✅ 全自動ローカライズが完了しました！", state="complete", expanded=False)
                
            st.subheader("📤 生成結果")
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown("##### 翻訳字幕 (SRT)")
                st.text_area("Translated SRT", value=translated_srt, height=280)
                st.download_button(
                    "💾 翻訳済み字幕を保存 (.srt)",
                    data=translated_srt,
                    file_name=f"translated_{media_file.name}.srt"
                )
            with col_res2:
                st.markdown("##### 日本語原文 (SRT)")
                st.text_area("Original SRT", value=raw_srt, height=280)
                st.download_button(
                    "📄 原文字幕を保存 (.srt)",
                    data=raw_srt,
                    file_name=f"original_{media_file.name}.srt"
                )
                
            if meta_result:
                st.markdown("---")
                st.subheader("🎯 YouTube運用パッケージ（タイトル・サムネ文・概要欄）")
                st.text_area("Metadata Pack", value=meta_result, height=250)

# ----------------- モード2: テキスト・台本コピペ -----------------
with tab2:
    st.subheader("長文テキスト / 既存SRT字幕のコピペ翻訳")
    st.caption("台本テキスト（日本語）や、すでに持っているSRT字幕を貼り付けるだけで、文脈を汲み取った高精度翻訳を行います。")
    
    text_input_type = st.radio("入力形式", ["通常の台本テキスト（日本語）", "SRT字幕ファイル（タイムコード付き）"], horizontal=True)
    raw_text = st.text_area("翻訳したい台本またはSRTテキストを貼り付け", height=200, placeholder="ここにテキストをペーストしてください...")
    
    gen_meta_text = st.checkbox("この台本からYouTube用タイトル・サムネ案も同時作成する", value=False, key="chk_text_meta")
    btn_text = st.button("🚀 テキストをネイティブ意訳", type="primary", key="btn_text")
    
    if btn_text:
        if not raw_text.strip():
            st.warning("⚠️ テキストを入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ サイドバーに「Anthropic API Key」を入力してください。")
        elif "ChatGPT" in engine and not openai_key:
            st.error("⚠️ サイドバーに「OpenAI API Key」を入力してください。")
        else:
            with st.spinner("文脈とニュアンスを分析し、自然な表現に翻訳中..."):
                sys_p = get_system_prompt(target_lang, channel_genre, custom_rule)
                if text_input_type == "SRT字幕ファイル（タイムコード付き）":
                    u_prompt = f"以下のSRT字幕のタイムコードを1文字も崩さず、テキスト部分のみをネイティブ向けに自然に翻訳してください:\n\n{raw_text}"
                else:
                    u_prompt = f"以下の日本語台本を、直訳を避けてネイティブが自然に共感できる口調に翻訳してください:\n\n{raw_text}"
                    
                result_text = call_ai(sys_p, u_prompt, engine, openai_key, claude_key, model_name)
                
                st.subheader("📤 翻訳結果")
                st.text_area("翻訳後テキスト", value=result_text, height=250)
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

# ----------------- モード3: 1文クイック入力 -----------------
with tab3:
    st.subheader("1文クイック翻訳（テロップ・サムネイル文字・煽り文句）")
    st.caption("「この日本語のニュアンス、英語で何て言うのが一番自然？」を1発で解決。複数の言い回し（スラング、丁寧、煽りなど）を同時提案します。")
    
    single_phrase = st.text_input("翻訳したい1フレーズ", placeholder="例: マジで許せないんだけど、これどう思う？ / 衝撃の結末を見逃すな")
    btn_single = st.button("🔍 複数の言い回し・ニュアンスを提案", type="primary", key="btn_single")
    
    if btn_single:
        if not single_phrase.strip():
            st.warning("⚠️ フレーズを入力してください。")
        elif "Claude" in engine and not claude_key:
            st.error("⚠️ サイドバーに「Anthropic API Key」を入力してください。")
        elif "ChatGPT" in engine and not openai_key:
            st.error("⚠️ サイドバーに「OpenAI API Key」を入力してください。")
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
