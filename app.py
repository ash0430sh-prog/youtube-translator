"""
TRANSLY PRO | Pure SRT Extractor & Premiere Pro One-Drop Ready (Format Selector Edition)
"""

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import tempfile
import os
import time
import re

st.set_page_config(
    page_title="TRANSLY PRO | 完全無料 AI動画ローカライズ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

# ホログラムサイバースタイルCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Noto+Sans+JP:wght@500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    header[data-testid="stHeader"] {
        background: rgba(5, 8, 17, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-bottom: 1px solid rgba(0, 242, 254, 0.25) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    header[data-testid="stHeader"] * {
        color: #38BDF8 !important;
    }
    header[data-testid="stHeader"] svg {
        fill: #38BDF8 !important;
        transition: all 0.2s ease;
    }
    header[data-testid="stHeader"] button:hover svg {
        fill: #00F2FE !important;
        filter: drop-shadow(0 0 8px #00F2FE);
    }
    [data-testid="stDecoration"] {
        display: none !important;
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
    
    textarea, [data-baseweb="textarea"] textarea {
        background-color: #090E1A !important;
        color: #F8FAFC !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        line-height: 1.6 !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        border-radius: 10px !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
    }
    textarea:focus, [data-baseweb="textarea"] textarea:focus {
        border-color: #00F2FE !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.4) !important;
    }
    [data-testid="stTextArea"] label {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
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

    [data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #050811 !important;
        padding: 0.45rem 0.2rem !important;
        font-size: 0.88rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.02em !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(0, 242, 254, 0.35) !important;
        margin-top: 4px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        filter: brightness(1.15) !important;
        box-shadow: 0 0 16px rgba(0, 242, 254, 0.6) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stSidebar"] div.stButton > button * {
        color: #050811 !important;
        font-weight: 900 !important;
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
        right: 40px;
        top: 14px;
        display: flex;
        flex-direction: column;
        align-items: center;
        pointer-events: none;
    }
    .holo-cube {
        width: 106px;
        height: 106px;
        position: relative;
        border: 2px solid rgba(0, 242, 254, 0.6);
        border-radius: 16px;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 20px rgba(0, 242, 254, 0.2);
        animation: holoFloat 3.8s ease-in-out infinite alternate;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 242, 254, 0.04);
    }
    .bot-head {
        width: 76px;
        height: 62px;
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border-radius: 18px;
        border: 2px solid #38BDF8;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4), inset 0 2px 4px rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        position: relative;
    }
    .bot-eye {
        width: 18px;
        height: 24px;
        background: radial-gradient(circle, #FFFFFF 20%, #00F2FE 70%, #0284C7 100%);
        border-radius: 50%;
        box-shadow: 0 0 14px #00F2FE, 0 0 24px #38BDF8;
        animation: botBlink 3.8s infinite ease-in-out;
    }
    .bot-blush-left, .bot-blush-right {
        position: absolute;
        bottom: 8px;
        width: 8px;
        height: 4px;
        background: rgba(244, 114, 182, 0.75);
        border-radius: 50%;
        filter: blur(1px);
    }
    .bot-blush-left { left: 8px; }
    .bot-blush-right { right: 8px; }
    
    .holo-base {
        width: 124px;
        height: 14px;
        background: linear-gradient(90deg, #64748B, #E2E8F0, #64748B);
        border-radius: 5px;
        margin-top: 10px;
        box-shadow: 0 0 18px rgba(0, 242, 254, 0.5);
    }
    
    @keyframes holoFloat {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-8px) rotate(2deg); }
        100% { transform: translateY(-12px) rotate(-2deg); }
    }
    @keyframes botBlink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.08); }
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
        max-width: 76%;
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

    .stMainBlockContainer div.stButton > button:first-child {
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
    .stMainBlockContainer div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 35px rgba(0, 242, 254, 0.65);
        filter: brightness(1.08);
    }
</style>
""", unsafe_allow_html=True)

def parse_srt_and_metadata(full_text):
    clean = re.sub(r'```(?:srt)?', '', full_text).strip()
    meta_split = re.search(r'(\n(?:【.*?】|##|###|\*\*[^\n]+\*\*).*)', clean, re.DOTALL)
    
    if meta_split and "-->" not in meta_split.group(1).split("\n")[1]:
        srt_part = clean[:meta_split.start()].strip()
        meta_part = meta_split.group(1).strip()
    else:
        srt_part = clean
        meta_part = ""
        
    return srt_part, meta_part

def srt_to_plain_text(srt_text):
    lines = srt_text.splitlines()
    text_lines = []
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.isdigit():
            continue
        if "-->" in line_s:
            continue
        text_lines.append(line_s)
    return "\n".join(text_lines)

def get_mime_type(file_name):
    ext = file_name.split('.')[-1].lower()
    mime_map = {
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'mp3': 'audio/mp3',
        'wav': 'audio/wav',
        'm4a': 'audio/mp4'
    }
    return mime_map.get(ext, 'video/mp4')

def discover_active_models(client):
    try:
        available = []
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "flash" in name.lower() and "thinking" not in name.lower():
                available.append(name)
        available.sort(reverse=True)
        return available if available else ["gemini-3.6-flash"]
    except Exception:
        return ["gemini-3.6-flash"]

# サイドバー
with st.sidebar:
    st.markdown("### ⚡ FREE AI KEY")
    st.caption("🎁 **完全無料（0円）で利用可能**")
    st.markdown("""
    Google AI Studioで即座に無料取得できます（クレカ不要）。  
    👉 [**無料APIキーを取得する**](https://aistudio.google.com/app/apikey)
    """)
    
    storage_sync_code = """
    <script>
    const saved = localStorage.getItem('transly_gemini_key');
    if (saved && !window.parent.location.hash.includes('loaded')) {
        const input = window.parent.document.querySelector('input[type="password"]');
        if (input && !input.value) {
            input.value = saved;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    </script>
    """
    components.html(storage_sync_code, height=0)
    
    gemini_key = st.text_input(
        "🔑 Google Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        placeholder="AQ... または AIza..."
    )
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        save_key_btn = st.button("💾 記憶", use_container_width=True)
    with col_k2:
        clear_key_btn = st.button("🗑️ 消去", use_container_width=True)
        
    if save_key_btn and gemini_key.strip():
        st.session_state.gemini_api_key = gemini_key.strip()
        js_save = f"""
        <script>
        localStorage.setItem('transly_gemini_key', '{gemini_key.strip()}');
        </script>
        """
        components.html(js_save, height=0)
        st.success("記憶完了！次回から自動ロードされます。")
        
    if clear_key_btn:
        st.session_state.gemini_api_key = ""
        js_clear = """
        <script>
        localStorage.removeItem('transly_gemini_key');
        </script>
        """
        components.html(js_clear, height=0)
        st.info("記憶したキーを消去しました。")

    st.divider()
    st.markdown("### 🌐 LOCALIZE CORE")
    
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "日本語 (自然な口語・スラング・テロップ調)",
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
            "⚡ ショート/リール/TikTok（超短縮・インパクト重視）",
            "🔥 YouTubeエンタメ・実況（テンポ重視・スラング適応）",
            "📖 2ch/修羅場/スカッと系（口語・感情爆発・テンポ良い煽り）",
            "👻 ホラー・怪談・ミステリー（情緒的・不穏・引き込まれる語り）",
            "💡 ビジネス・解説・教養（分かりやすく知的な口調）"
        ]
    )
    
    custom_rule = st.text_area(
        "個別ルール・固有名詞（任意）",
        placeholder="例: 若者言葉を意識して。Hit me upは『連絡して！』のようにテンポ良く訳して。"
    )

def get_system_instruction(lang, genre, custom):
    return f"""あなたは世界トップレベルの映像翻訳・ローカライズディレクターです。

【最重要ミッション】
「直訳」を徹底的に排除してください。
直訳特有の硬さや不自然さをなくし、YouTubeやTikTokの視聴者が一瞬で理解して共感・笑える自然な表現（スラング、若者言葉、テンポの良い言い回し）に意訳してください。

対象言語: {lang}
動画ジャンル: {genre}
ルール: {custom if custom else "なし"}
"""

def execute_with_auto_healing(client, contents, sys_inst):
    active_models = discover_active_models(client)
    last_exception = None
    
    for model_name in active_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(system_instruction=sys_inst)
                )
                return response.text
            except Exception as e:
                last_exception = e
                err_str = str(e)
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break
                elif "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2)
                    continue
                else:
                    break
    raise last_exception

# メインヘッダー
st.markdown("""
<div class="hero-container">
    <div class="holo-wrapper">
        <div class="holo-cube">
            <div class="bot-head">
                <div class="bot-eye"></div>
                <div class="bot-eye"></div>
                <div class="bot-blush-left"></div>
                <div class="bot-blush-right"></div>
            </div>
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

# ----------------- モード1: 動画投入 -----------------
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
    
    st.markdown("##### ⚙️ 同時に作成するコンテンツを選択")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        opt_title = st.checkbox("🎯 クリック率特化タイトル案 (3選)", value=False)
    with col_c2:
        opt_thumb = st.checkbox("🖼️ サムネイル用キャッチコピー", value=False)
    with col_c3:
        opt_desc = st.checkbox("📝 概要欄 ＆ ハッシュタグ", value=False)
        
    btn_video = st.button("⚡ 無料AIで動画を解析・ローカライズ開始", type="primary", key="btn_v")
    
    active_key = gemini_key.strip() or st.session_state.gemini_api_key
    
    if btn_video:
        if not active_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not media_file:
            st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
        else:
            with st.status("🤖 ホログラムAIが完全無料でメディアを処理中...", expanded=True) as status:
                st.write("📦 1/3 ファイルを展開・一時保存中...")
                mime_type = get_mime_type(media_file.name)
                _, ext = os.path.splitext(media_file.name)
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(media_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    client = genai.Client(api_key=active_key)
                    st.write("☁️ 2/3 Googleサーバーへ転送・インデックス待機中...")
                    
                    uploaded_file = client.files.upload(file=tmp_path)
                    
                    wait_count = 0
                    while uploaded_file.state.name == "PROCESSING" and wait_count < 40:
                        time.sleep(3)
                        uploaded_file = client.files.get(name=uploaded_file.name)
                        wait_count += 1
                        
                    if uploaded_file.state.name == "FAILED":
                        raise ValueError("動画解析処理に失敗しました。")
                    
                    st.write("🌐 3/3 音声を解析し、字幕データを生成中...")
                    
                    prompt = f"""動画内の会話音声を認識し、以下の指示に従って出力してください。
【厳格なフォーマット指示】
1. 最初は必ず純粋なSRT字幕形式のみを出力してください（マークダウンの```srt記法や前置きの挨拶文は一切不要）。
2. 各字幕は「番号」「タイムコード（00:00:00,000 --> 00:00:00,000）」「テキスト」の3行構成を厳守してください。
3. 日本語の直訳を完全に避け、{target_lang}のYouTube/TikTokネイティブが使う自然な口語・スラングに意訳してください。
"""
                    extras = []
                    if opt_title:
                        extras.append("- 【クリック率特化タイトル案 3選】")
                    if opt_thumb:
                        extras.append("- 【サムネイル用キャッチコピー】")
                    if opt_desc:
                        extras.append("- 【概要欄・ハッシュタグ】")
                        
                    if extras:
                        prompt += "\n【追加生成項目（※すべてのSRT字幕が終わった後に空行を空けて記載してください）】\n" + "\n".join(extras)
                        
                    raw_result = execute_with_auto_healing(
                        client=client,
                        contents=[uploaded_file, prompt],
                        sys_inst=get_system_instruction(target_lang, channel_genre, custom_rule)
                    )
                    status.update(label="✨ 完全無料でのローカライズが完了しました！", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"エラー詳細: {e}")
                    raw_result = ""
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        
            if raw_result:
                srt_data, meta_data = parse_srt_and_metadata(raw_result)
                plain_text_data = srt_to_plain_text(srt_data)
                base_name = os.path.splitext(media_file.name)[0]
                
                st.markdown("### 📥 保存形式の選択")
                download_format = st.radio(
                    "保存するファイル形式を選択してください：",
                    [
                        "🎬 Premiere Pro / CapCut 編集用 (.srt)",
                        "📄 読み物・台本用プレーンテキスト (.txt)",
                        "📦 両方（SRT ＆ TXT）"
                    ],
                    horizontal=True
                )
                
                if "両方" in download_format:
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.download_button(
                            label="📥 編集用字幕 (.srt) を保存",
                            data=srt_data,
                            file_name=f"{base_name}_subtitles.srt",
                            mime="application/x-subrip",
                            use_container_width=True
                        )
                    with col_b2:
                        st.download_button(
                            label="📄 テキスト台本 (.txt) を保存",
                            data=plain_text_data,
                            file_name=f"{base_name}_script.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                elif ".srt" in download_format:
                    st.download_button(
                        label="📥 編集用字幕 (.srt) を保存 (Premiere / CapCut対応)",
                        data=srt_data,
                        file_name=f"{base_name}_subtitles.srt",
                        mime="application/x-subrip",
                        use_container_width=True
                    )
                else:
                    st.download_button(
                        label="📄 テキスト台本 (.txt) を保存 (タイムコードなし)",
                        data=plain_text_data,
                        file_name=f"{base_name}_script.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                if meta_data:
                    st.download_button(
                        label="📝 YouTube運用メタデータ (.txt) を保存",
                        data=meta_data,
                        file_name=f"{base_name}_metadata.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                st.markdown("#### プレビュー確認")
                tab_p1, tab_p2 = st.tabs(["🎬 SRT字幕プレビュー", "📄 テキストプレビュー"])
                with tab_p1:
                    st.text_area("SRT Content", value=srt_data, height=240)
                with tab_p2:
                    st.text_area("Plain Text Content", value=plain_text_data, height=240)
                
                if meta_data:
                    st.markdown("#### 📝 YouTube運用メタデータ")
                    st.text_area("Metadata Content", value=meta_data, height=160)

# ----------------- モード2: 台本コピペ -----------------
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
    
    text_input_type = st.radio("入力するデータの形式", ["台本テキスト（通常の文章）", "SRT字幕ファイル（タイムコード付き）"], horizontal=True)
    raw_text = st.text_area("台本またはSRT字幕をペースト", height=180, placeholder="テキストを貼り付けてください...")
    
    st.markdown("##### ⚙️ 同時に作成するコンテンツを選択")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        opt_title_t = st.checkbox("🎯 タイトル案 (3選)", value=False, key="chk_tt")
    with col_t2:
        opt_thumb_t = st.checkbox("🖼️ サムネイル用キャッチコピー", value=False, key="chk_th")
        
    btn_text = st.button("🚀 無料AIでテキストをネイティブ意訳する", type="primary", key="btn_t")
    
    if btn_text:
        if not active_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not raw_text.strip():
            st.warning("⚠️ テキストを入力してください。")
        else:
            with st.spinner("🤖 Geminiが文脈とスラングを考慮して自然に翻訳中..."):
                try:
                    client = genai.Client(api_key=active_key)
                    if "SRT" in text_input_type:
                        u_prompt = f"以下のSRT字幕のタイムコードを正確に維持し、テキスト部分のみを{target_lang}向けに自然に意訳してください。マークダウンの```記法や前置きは出力せず、純粋なSRT形式のみを出力してください:\n\n{raw_text}"
                    else:
                        u_prompt = f"以下の台本を、直訳を避けて{target_lang}向けに自然な口調に翻訳してください:\n\n{raw_text}"
                        
                    t_extras = []
                    if opt_title_t:
                        t_extras.append("- 【クリック率特化タイトル案 3選】")
                    if opt_thumb_t:
                        t_extras.append("- 【サムネイル用キャッチコピー】")
                    if t_extras:
                        u_prompt += "\n\n末尾に以下を追加してください：\n" + "\n".join(t_extras)
                        
                    res_text = execute_with_auto_healing(
                        client=client,
                        contents=u_prompt,
                        sys_inst=get_system_instruction(target_lang, channel_genre, custom_rule)
                    )
                    
                    if "SRT" in text_input_type:
                        s_part, m_part = parse_srt_and_metadata(res_text)
                        plain_part = srt_to_plain_text(s_part)
                        
                        st.markdown("### 📥 保存形式を選択")
                        m2_format = st.radio("保存形式：", ["🎬 SRT字幕ファイル (.srt)", "📄 テキスト台本 (.txt)", "📦 両方"], horizontal=True, key="rad_m2")
                        
                        if "両方" in m2_format:
                            col_sub1, col_sub2 = st.columns(2)
                            with col_sub1:
                                st.download_button("📥 字幕 (.srt) を保存", data=s_part, file_name="translated.srt", mime="application/x-subrip", use_container_width=True)
                            with col_sub2:
                                st.download_button("📄 台本 (.txt) を保存", data=plain_part, file_name="translated.txt", mime="text/plain", use_container_width=True)
                        elif ".srt" in m2_format:
                            st.download_button("📥 字幕 (.srt) を保存", data=s_part, file_name="translated.srt", mime="application/x-subrip", use_container_width=True)
                        else:
                            st.download_button("📄 台本 (.txt) を保存", data=plain_part, file_name="translated.txt", mime="text/plain", use_container_width=True)
                            
                        st.text_area("出力プレビュー", value=s_part, height=240)
                    else:
                        st.markdown("### 📥 翻訳結果")
                        st.text_area("Translated Output", value=res_text, height=280)
                        st.download_button("💾 翻訳結果を保存 (.txt)", data=res_text, file_name="translated_script.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"エラー詳細: {e}")

# ----------------- モード3: 1文クイック -----------------
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
    
    single_phrase = st.text_input("翻訳したいフレーズを入力", placeholder="例: Hit me up / マジで許せないんだけど、これどう思う？")
    btn_single = st.button("⚡ 複数の表現・スラングを提案", type="primary", key="btn_s")
    
    if btn_single:
        if not active_key:
            st.error("⚠️ 左側サイドバーにGoogle Geminiの無料APIキーを入力してください。")
        elif not single_phrase.strip():
            st.warning("⚠️ フレーズを入力してください。")
        else:
            with st.spinner("🤖 Geminiが複数の言い回しを考案中..."):
                try:
                    client = genai.Client(api_key=active_key)
                    single_prompt = f"""以下のフレーズについて、直訳ではなくYouTubeネイティブが使う以下の4パターンを出力してください：
フレーズ: 「{single_phrase}」
対象言語: {target_lang}
ジャンル: {channel_genre}

1. **スラング・カジュアル（感情的・リアルな若者言葉）**
2. **サムネイル用（2〜3単語で目立つ超短縮インパクト表現）**
3. **ナチュラル標準（誰にでも通じる自然な日常会話）**
4. **解説（ニュアンスの違いを1行で）**
"""
                    res_text = execute_with_auto_healing(
                        client=client,
                        contents=single_prompt,
                        sys_inst=get_system_instruction(target_lang, channel_genre, custom_rule)
                    )
                    st.markdown("### 💡 提案結果")
                    st.markdown(res_text)
                except Exception as e:
                    st.error(f"エラー詳細: {e}")
