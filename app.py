"""
TRANSLY PRO | Universal SRT & TXT Format Selector
- 台本テキスト入力時でも「編集用SRT字幕 / 読み物用TXT / 両方」を選択可能
- Geminiが文章量に応じて自然なタイムコードを自動配分
- Premiere Pro / CapCut 等のタイムラインへ即座に配置可能
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

def plain_text_to_srt(plain_text):
    lines = [l.strip() for l in plain_text.splitlines() if l.strip()]
    srt_blocks = []
    current_sec = 0
    for idx, text in enumerate(lines, start=1):
        start_m, start_s = divmod(current_sec, 60)
        end_sec = current_sec + 3
        end_m, end_s = divmod(end_sec, 60)
        time_str = f"00:{start_m:02d}:{start_s:02d},000 --> 00:{end_m:02d}:{end_s:02d},000"
        srt_blocks.append(f"{idx}\n{time_str}\n{text}\n")
        current_sec += 3
    return "\n".join(srt_blocks)

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
