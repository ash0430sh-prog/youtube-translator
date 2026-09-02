"""
TRANSLY PRO | Gemini 100% Free Core Edition
- Google AI Studio (Gemini 2.5 Flash / 1.5 Flash) 無料APIキー対応
- クレジットカード登録不要・完全0円で動画/音声の文字起こし・ネイティブ翻訳・YouTubeマーケ素材生成が可能
- 前回のホログラムAIロボットUIをそのまま完全継承
"""

import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(
    page_title="TRANSLY PRO | 完全無料 AI動画ローカライズ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ホログラムサイバースタイルCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Noto+Sans+JP:wght@500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif;
    }
    
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

# サイドバー（Gemini 100%無料キー）
with st.sidebar:
    st.markdown("### ⚡ FREE AI KEY")
    st.caption("🎁 **完全無料（0円）で利用可能**")
    st.markdown("""
    Google AI Studioで即座に無料取得できます（クレカ不要）。  
    👉 [**無料APIキーを取得する**](https://aistudio.google.com/app/apikey)
    """)
    
    gemini_key = st.text_input("🔑 Google Gemini API Key", type="password", placeholder="AIzaSy...")
    model_choice = st.selectbox(
        "🧠 搭載モデル（すべて完全無料）",
        ["gemini-2.5-flash (超高速・動画認識・最新)", "gemini-1.5-flash (高精度・大容量対応)"]
    )
    
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

def get_system_instruction(lang, genre, custom):
    return f"""あなたは世界トップレベルのYouTube映像翻訳ディレクターです。
【最重要ミッション】
「直訳」を徹底的に排除してください。
直訳英語特有の硬さや不自然さをなくし、ネイティブYouTuberが普段のテンションで喋っている、あるいは日本人が聞いても納得できる自然なスラング・日常会話表現に意訳してください。

対象言語: {lang}
動画ジャンル: {genre}
ルール: {custom if custom else "なし"}
"""

# Gemini API呼び出し
def run_gemini(api_key, model_str, prompt, parts=[]):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_str.split()[0],
        system_instruction=get_system_instruction(target_lang, channel_genre, custom_rule)
    )
    content = parts + [prompt]
    res = model.generate_content(content)
    return res.text

# メインヘッダー
st.markdown("""
<div class="hero-container">
    <div class="holo-wrapper">
        <div class="holo-cube">
            <div class="holo-eyes">👀</div>
        </div>
        <div class="holo-base"></div>
    </div>
    <div class="hero-badge">⚡ 100% FREE AI CORE</div>
    <div class="hero-title">TRANSLY PRO 完全無料ローカライズ</div>
    <div class="hero-desc">追加課金・クレカ登録ゼロ！Google公式の完全無料枠で、動画直接投入から字幕SRT・タイトル案・サムネ英文まで一撃生成します。</div>
</div>
""", unsafe_allow_html=True)

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
            <span class="step-title">動画または音声ファイルをアップロード（完全無料）</span>
        </div>
        <p style="font-size:0.88rem; color:#94A3B8; margin: 4px 0 0 0;">MP4 / MOV / MP3 などを入れるだけで、Geminiが直接動画・音声を認識してネイティブ字幕を生成します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    media_file = st.file_uploader("動画・音声ファイルをドロップ", type=["mp4", "mov", "mp3", "wav", "m4a"], key="u_media")
    gen_meta_video = st.checkbox("🎯 海外向けタイトル3案・概要欄・サムネ用コピーも同時生成する", value=True)
    btn_video = st.button("⚡ 無料AIで動画を自動解析・翻訳開始", type="primary", key="btn_v")
    
    if btn_video:
        if not gemini_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not media_file:
            st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
        else:
            with st.status("🤖 ホログラムAIが完全無料でメディアを直接処理中...", expanded=True) as status:
                st.write("📤 1/2 動画・音声データをGeminiへ安全に一時転送中...")
                _, ext = os.path.splitext(media_file.name)
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(media_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    genai.configure(api_key=gemini_key)
                    uploaded_file = genai.upload_file(path=tmp_path)
                    
                    st.write("🌐 2/2 音声を直接解析し、ネイティブ字幕(SRT)＆YouTubeメタデータを生成中...")
                    prompt = f"""アップロードされたメディアの音声を認識し、以下の指示に従って出力してください。
1. 日本語の会話を直訳せず、{target_lang}のYouTubeネイティブが使う自然な日常会話・スラングに意訳したSRT形式の字幕データを出力してください。
2. タイムコードは正確に付与してください。
"""
                    if gen_meta_video:
                        prompt += f"""
3. さらに動画の最後（または字幕の後）に、以下のYouTube運用パッケージを記載してください：
- 【クリック率特化タイトル案 3選】
- 【サムネイル用英語キャッチコピー（2〜4単語）】
- 【SEO最適化概要欄】
"""
                    result_text = run_gemini(gemini_key, model_choice, prompt, parts=[uploaded_file])
                    status.update(label="✨ 完全無料でのローカライズが完了しました！", state="complete", expanded=False)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        
            st.markdown("### 📥 生成された結果")
            st.text_area("Gemini Output (SRT & Metadata)", value=result_text, height=350)
            st.download_button(
                "💾 結果データをダウンロード (.srt / .txt)",
                data=result_text,
                file_name=f"free_translated_{media_file.name}.srt"
            )

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
    btn_text = st.button("🚀 無料AIでテキストをネイティブ意訳する", type="primary", key="btn_t")
    
    if btn_text:
        if not gemini_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not raw_text.strip():
            st.warning("⚠️ テキストを入力してください。")
        else:
            with st.spinner("🤖 Geminiが文脈とスラングを考慮して自然に翻訳中..."):
                if "SRT" in text_input_type:
                    u_prompt = f"以下のSRT字幕のタイムコードを崩さず、テキスト部分のみをネイティブ向けに自然に翻訳してください:\n\n{raw_text}"
                else:
                    u_prompt = f"以下の日本語台本を、直訳を避けてネイティブが自然に共感できる口調に翻訳してください:\n\n{raw_text}"
                if gen_meta_text:
                    u_prompt += "\n\nさらにクリックされる英語タイトル3案とサムネ用コピーを末尾に提案してください。"
                    
                res_txt = run_gemini(gemini_key, model_choice, u_prompt)
                st.markdown("### 📥 翻訳結果")
                st.text_area("Translated Output", value=res_txt, height=280)
                st.download_button("💾 翻訳結果を保存 (.txt)", data=res_txt, file_name="translated_script.txt")

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
        if not gemini_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not single_phrase.strip():
            st.warning("⚠️ フレーズを入力してください。")
        else:
            with st.spinner("🤖 Geminiが複数の言い回しを考案中..."):
                single_prompt = f"""以下の日本語フレーズについて、直訳ではなくYouTubeネイティブが使う以下の4パターンを出力してください：
フレーズ: 「{single_phrase}」
言語: {target_lang}
動画ジャンル: {channel_genre}

1. **YouTubeスラング・カジュアル（感情的・リアルな若者言葉）**
2. **サムネイル用（2〜3単語で目立つ超短縮インパクト表現）**
3. **ナチュラル標準（誰にでも通じる自然な日常会話）**
4. **解説（日本語とのニュアンスの違いを1行で）**
"""
                res_single = run_gemini(gemini_key, model_choice, single_prompt)
                st.markdown("### 💡 提案結果")
                st.markdown(res_single)
