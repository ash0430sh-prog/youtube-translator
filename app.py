"""
TRANSLY PRO | AI Video Localization System
- Cyberpunk Full Dark Theme (Unified Sidebar Styling)
- 3D Core Interface
- Freemium License Protection (Supabase Integration)
"""

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import tempfile
import os
import time
import re

# Supabase Client setup
supabase_client = None
try:
    from supabase import create_client, Client
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        supabase_client: Client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
except Exception:
    pass

st.set_page_config(
    page_title="TRANSLY PRO | 次世代AI動画ローカライズ",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "license_key" not in st.session_state:
    st.session_state.license_key = ""
if "is_pro_active" not in st.session_state:
    st.session_state.is_pro_active = False
if "m1_result" not in st.session_state:
    st.session_state.m1_result = None
if "m2_result" not in st.session_state:
    st.session_state.m2_result = None

# 共通CSSスタイル（サイドバー完全ダーク・サイバー化）
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@400;600;800&display=swap');
    
    /* アプリ全体背景 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0c162d 0%, #050811 80%);
        color: #E2E8F0;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* 🌙 サイドバーの完全ダーク・サイバーカラー化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090e1b 0%, #050811 100%) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.25) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.6);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(0, 242, 254, 0.18) !important;
    }

    /* 入力フォームのサイバー調スタイル */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #0d1527 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: #00F2FE !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.4) !important;
    }

    /* サイドバーのボタン */
    [data-testid="stSidebar"] button {
        background: #0f1c36 !important;
        color: #7DD3FC !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(0, 242, 254, 0.2) !important;
        border-color: #00F2FE !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.5) !important;
    }

    .hero-container {
        padding: 5px 0 15px 0;
        border-bottom: 1px solid rgba(0, 242, 254, 0.2);
        margin-bottom: 20px;
    }
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        letter-spacing: 0.12em;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #8E2DE2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 25px rgba(0, 242, 254, 0.4);
        margin-bottom: 4px;
    }
    .hero-sub {
        font-family: 'Share Tech Mono', monospace;
        color: #7DD3FC;
        font-size: 0.92rem;
        letter-spacing: 0.08em;
    }

    .pro-badge-active {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF;
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        font-size: 0.8rem;
        padding: 6px 14px;
        border-radius: 6px;
        letter-spacing: 0.1em;
        display: block;
        text-align: center;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
    }
    
    .free-badge {
        background: rgba(148, 163, 184, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.25);
        color: #94A3B8;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 0.76rem;
        padding: 6px 10px;
        border-radius: 6px;
        display: block;
        text-align: center;
        letter-spacing: 0.05em;
    }

    /* ロックカード */
    .cyber-lock-box {
        background: linear-gradient(180deg, rgba(13, 22, 44, 0.85) 0%, rgba(5, 10, 22, 0.95) 100%);
        border: 1px solid rgba(0, 242, 254, 0.35);
        box-shadow: 0 0 35px rgba(0, 242, 254, 0.12), inset 0 0 30px rgba(0, 242, 254, 0.04);
        border-radius: 16px;
        padding: 30px 24px 35px 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-top: 15px;
    }
    .cyber-lock-box::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #00F2FE, #8E2DE2, transparent);
    }
    .lock-hud-tag {
        font-family: 'Share Tech Mono', monospace;
        color: #FF0055;
        font-size: 0.82rem;
        letter-spacing: 0.15em;
        margin-bottom: 8px;
        display: inline-block;
    }
    .lock-hud-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1.6rem;
        letter-spacing: 0.08em;
        color: #FFFFFF;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
        margin-bottom: 12px;
    }
    .lock-hud-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        max-width: 620px;
        margin: 0 auto 24px auto;
        line-height: 1.7;
    }
    .feature-chips {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 25px;
    }
    .chip {
        background: rgba(0, 242, 254, 0.08);
        border: 1px solid rgba(0, 242, 254, 0.25);
        color: #7DD3FC;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        padding: 6px 14px;
        border-radius: 20px;
    }
    .api-link-box {
        background: rgba(0, 242, 254, 0.07);
        border-left: 3px solid #00F2FE;
        padding: 10px 12px;
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 8px;
        margin-bottom: 12px;
        border-radius: 0 8px 8px 0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# 3D AI Robot コンポーネント
def render_cyber_robot(height=310):
    robot_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          margin: 0;
          overflow: hidden;
          background: transparent;
          display: flex;
          align-items: center;
          justify-content: center;
        }}
        canvas {{
          display: block;
          filter: drop-shadow(0 0 20px rgba(0, 242, 254, 0.45));
        }}
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
      <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5.4;
        camera.position.y = 0.0;

        const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        const coreGroup = new THREE.Group();
        scene.add(coreGroup);

        const sphereGeo = new THREE.SphereGeometry(1.15, 24, 24);
        const sphereMat = new THREE.MeshBasicMaterial({{
          color: 0x00F2FE,
          wireframe: true,
          transparent: true,
          opacity: 0.35
        }});
        const outerSphere = new THREE.Mesh(sphereGeo, sphereMat);
        coreGroup.add(outerSphere);

        const coreGeo = new THREE.IcosahedronGeometry(0.68, 1);
        const coreMat = new THREE.MeshStandardMaterial({{
          color: 0x8E2DE2,
          roughness: 0.2,
          metalness: 0.8,
          emissive: 0x00F2FE,
          emissiveIntensity: 0.65
        }});
        const coreMesh = new THREE.Mesh(coreGeo, coreMat);
        coreGroup.add(coreMesh);

        const ring1Geo = new THREE.TorusGeometry(1.5, 0.02, 16, 100);
        const ring1Mat = new THREE.MeshBasicMaterial({{ color: 0x00F2FE, transparent: true, opacity: 0.85 }});
        const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
        coreGroup.add(ring1);

        const ring2Geo = new THREE.TorusGeometry(1.68, 0.015, 16, 100);
        const ring2Mat = new THREE.MeshBasicMaterial({{ color: 0xFF007F, transparent: true, opacity: 0.7 }});
        const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
        coreGroup.add(ring2);

        const light = new THREE.PointLight(0x00F2FE, 2.2, 50);
        light.position.set(5, 5, 5);
        scene.add(light);
        const light2 = new THREE.PointLight(0xFF007F, 1.8, 50);
        light2.position.set(-5, -5, -2);
        scene.add(light2);
        scene.add(new THREE.AmbientLight(0x222233));

        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {{
          mouseX = (e.clientX / window.innerWidth - 0.5) * 1.5;
          mouseY = (e.clientY / window.innerHeight - 0.5) * 1.5;
        }});

        function animate() {{
          requestAnimationFrame(animate);
          coreGroup.rotation.y += 0.008;
          coreGroup.rotation.x += 0.004;

          ring1.rotation.x += 0.012;
          ring1.rotation.y += 0.007;

          ring2.rotation.z += 0.015;
          ring2.rotation.x += 0.009;

          coreGroup.rotation.y += (mouseX - coreGroup.rotation.y) * 0.04;
          coreGroup.rotation.x += (-mouseY - coreGroup.rotation.x) * 0.04;

          renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
        }});
      </script>
    </body>
    </html>
    """
    components.html(robot_html, height=height)

# Supabaseによるライセンス検証関数
def verify_license(key_str: str) -> bool:
    if not key_str or not supabase_client:
        return False
    try:
        res = supabase_client.table("transly_licenses").select("*").eq("license_key", key_str.strip()).execute()
        if res.data and len(res.data) > 0:
            rec = res.data[0]
            if rec.get("status") == "active":
                return True
    except Exception as e:
        st.sidebar.error(f"License Auth Error: {e}")
    return False

# ==========================================
# サイドバー設定
# ==========================================
with st.sidebar:
    st.markdown("### 👾 TRANSLY CONSOLE")
    
    st.markdown("#### 💎 PRO 会員認証")
    input_license = st.text_input(
        "ライセンスキー (PRO会員用)",
        value=st.session_state.license_key,
        type="password",
        help="サブスク決済完了時に発行されたキーを入力してください"
    )
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("🔑 認証する", use_container_width=True):
            if input_license:
                st.session_state.license_key = input_license.strip()
                if verify_license(st.session_state.license_key):
                    st.session_state.is_pro_active = True
                    st.success("PRO認証完了！")
                else:
                    st.session_state.is_pro_active = False
                    st.error("無効なキーです")
                st.rerun()
    with col_l2:
        if st.button("クリア", use_container_width=True):
            st.session_state.license_key = ""
            st.session_state.is_pro_active = False
            st.rerun()

    if st.session_state.is_pro_active:
        st.markdown('<div class="pro-badge-active">PRO ACTIVE 🔓 解放中</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="free-badge">FREE PLAN (MODE 2 & 3 利用可能)</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # 無料APIキー誘導セクション
    st.markdown("#### 🔑 Gemini API Key (完全無料・0円)")
    user_key = st.text_input("Google AI Studio Key", value=st.session_state.gemini_api_key, type="password")
    if user_key:
        st.session_state.gemini_api_key = user_key.strip()
    
    st.markdown("""
    <div class="api-link-box">
        💡 <strong>Gemini APIはクレカ不要・完全無料</strong>で誰でも即座に取得可能です。<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00F2FE; font-weight:bold; text-decoration:underline;">
            👉 Google AI Studio で無料APIキーを発行
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 🌐 ローカライズ設定")
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "日本語 (自然なYouTube口語・エンタメ風)",
            "日本語 (ビジネス / 解説・丁寧)",
            "英語 (US日常会話 / スラング)",
            "英語 (ビジネス / 丁寧)",
            "韓国語 (日常会話 / トレンド)",
            "繁体字中国語 (台湾 / 香港)",
            "簡体字中国語",
            "スペイン語",
            "タイ語",
            "インドネシア語"
        ]
    )
    video_genre = st.selectbox(
        "動画ジャンル・世界観",
        ["⚡ ショート/リール/TikTok (短縮重視)", "🔥 YouTubeエンタメ・実況 (テンポ重視)", "📖 2ch/修羅場/スカッと系 (煽り重視)", "🎓 解説・ビジネス・教養"]
    )
    custom_rule = st.text_area("個別ルール・固有名詞 (任意)", placeholder="例: 専門用語の指定やトーンの調整")

# ヘルパー関数
def srt_to_plain_text(srt_content: str) -> str:
    lines = srt_content.strip().split('\n')
    text_lines = []
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.isdigit() or '-->' in line_clean:
            continue
        text_lines.append(line_clean)
    return '\n'.join(text_lines)

def plain_text_to_srt(text_content: str) -> str:
    lines = [l.strip() for l in text_content.strip().split('\n') if l.strip()]
    srt_blocks = []
    current_sec = 0
    for idx, line in enumerate(lines, 1):
        start_sec = current_sec
        end_sec = current_sec + 3
        s_m, s_s = divmod(start_sec, 60)
        s_h, s_m = divmod(s_m, 60)
        e_m, e_s = divmod(end_sec, 60)
        e_h, e_m = divmod(e_m, 60)
        start_ts = f"{s_h:02d}:{s_m:02d}:{s_s:02d},000"
        end_ts = f"{e_h:02d}:{e_m:02d}:{e_s:02d},000"
        srt_blocks.append(f"{idx}\n{start_ts} --> {end_ts}\n{line}\n")
        current_sec += 3
    return '\n'.join(srt_blocks)

def get_system_prompt():
    return f"""あなたは世界最高峰の動画ローカライズディレクターです。
ターゲット言語: {target_lang}
動画ジャンル: {video_genre}
個別指定ルール: {custom_rule}

【厳守原則】
- 直訳は厳禁。ターゲット言語圏のネイティブがショート動画やYouTubeで自然に使う口語・スラング・言い回しに翻訳すること。
- 日本語へ翻訳する場合は、海外動画特有の硬い翻訳調を徹底排除し、日本のトップYouTuberが喋っているようなテンポ良い自然な日本語にすること。
- 字幕は1行あたり短く保ち、スマホ画面で一瞬で読めるリズムにすること。
"""

# ==========================================
# メイン画面ヘッダー
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">TRANSLY PRO // NEURAL LOCALIZE</div>
    <div class="hero-sub">> HIGH-PRECISION MULTI-MODAL TRANSLATION ENGINE & AUTO SRT COMPILER</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🎬 MODE 1: メディア直接解析 (PRO)",
    "📋 MODE 2: 台本・SRTコピペ (FREE)",
    "⚡ MODE 3: 1文クイック提案 (FREE)"
])

# ----------------------------------------------------
# TAB 1: 動画・音声直接投入 (PRO限定)
# ----------------------------------------------------
with tab1:
    render_cyber_robot(height=310)

    if not st.session_state.is_pro_active:
        st.markdown("""
        <div class="cyber-lock-box">
            <div class="lock-hud-tag">// SECURITY PROTOCOL: RESTRICTED ACCESS</div>
            <div class="lock-hud-title">PRO SPECIFICATION LOCKED</div>
            <div class="lock-hud-desc">
                動画・音声ファイル（MP4 / MOV / MP3）からの<strong>自動文字起こし・タイムコード同期SRT生成</strong>はPRO専用エンジンです。<br>
                テキスト台本翻訳（MODE 2）やフレーズ提案（MODE 3）は、無料プランのまま現在すぐにご利用いただけます。
            </div>
            <div class="feature-chips">
                <span class="chip">✔ MP4/MOV/MP3 ダイレクトインジェクション</span>
                <span class="chip">✔ 0.1秒単位のタイムコード完全同期</span>
                <span class="chip">✔ 3パターン CTR最適化タイトル生成</span>
            </div>
            <p style="color:#00F2FE; font-family:'Share Tech Mono', monospace; font-size:0.9rem;">
                >> PROプラン加入後、サイドバーのライセンスキー入力で即座にアンロックされます。
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("#### 🎬 メディアファイルを直接インジェクション")
        uploaded_file = st.file_uploader("動画・音声を選択 (MP4, MOV, MP3)", type=["mp4", "mov", "mp3", "m4a", "wav"])
        gen_meta = st.checkbox("クリック率特化タイトル案・サムネ英文・概要欄も同時生成する", value=True)
        
        if st.button("⚡ 動画を解析してローカライズ実行", type="primary", use_container_width=True):
            if not st.session_state.gemini_api_key:
                st.error("左サイドバーに Gemini API Key を入力してください。")
            elif not uploaded_file:
                st.warning("メディアファイルをアップロードしてください。")
            else:
                try:
                    with st.spinner("AIが動画を解析中..."):
                        client = genai.Client(api_key=st.session_state.gemini_api_key)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        uploaded_media = client.files.upload(file=tmp_path)
                        while uploaded_media.state.name == "PROCESSING":
                            time.sleep(4)
                            uploaded_media = client.files.get(name=uploaded_media.name)
                        
                        prompt = f"{get_system_prompt()}\n\nこの動画の音声を正確に文字起こしし、指定言語へ意訳した完全なSRT字幕を出力してください。"
                        if gen_meta:
                            prompt += "\nまた、冒頭に【TITLE_IDEAS】として引きの強いタイトル案3選とサムネ用キャッチコピーを出力してください。"

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[uploaded_media, prompt]
                        )
                        st.session_state.m1_result = response.text
                        st.success("ローカライズ完了！")
                except Exception as e:
                    st.error(f"解析エラー: {e}")

        if st.session_state.m1_result:
            st.markdown("### 📥 生成結果・ダウンロード")
            fmt = st.radio("保存形式を選択", ["🎬 Premiere Pro / CapCut 編集用 (.srt)", "📄 プレーンテキスト台本 (.txt)", "📦 両方"], key="m1_fmt")
            raw_text = st.session_state.m1_result
            srt_part = raw_text
            txt_part = srt_to_plain_text(raw_text)

            if fmt == "🎬 Premiere Pro / CapCut 編集用 (.srt)":
                st.download_button("💾 SRTファイルを保存", data=srt_part, file_name="localized_subtitles.srt", mime="text/plain")
            elif fmt == "📄 プレーンテキスト台本 (.txt)":
                st.download_button("💾 TXT台本を保存", data=txt_part, file_name="script.txt", mime="text/plain")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("💾 SRTファイルを保存", data=srt_part, file_name="localized_subtitles.srt", mime="text/plain", use_container_width=True)
                with c2:
                    st.download_button("💾 TXT台本を保存", data=txt_part, file_name="script.txt", mime="text/plain", use_container_width=True)
            
            with st.expander("プレビュー表示", expanded=True):
                st.text_area("出力内容", value=raw_text, height=350)

# ----------------------------------------------------
# TAB 2: 台本・SRTコピペ翻訳 (FREEプラン解放)
# ----------------------------------------------------
with tab2:
    st.markdown("#### 📋 台本テキスト / SRT字幕 コピペ翻訳（無料）")
    input_text = st.text_area("翻訳したい台本またはSRT字幕を貼り付け", height=200)
    
    if st.button("🚀 無料AIでネイティブ意訳する", type="primary", use_container_width=True):
        if not st.session_state.gemini_api_key:
            st.error("左サイドバーに Gemini API Key を入力してください。")
        elif not input_text.strip():
            st.warning("テキストを入力してください。")
        else:
            try:
                with st.spinner("AIが意訳中..."):
                    client = genai.Client(api_key=st.session_state.gemini_api_key)
                    prompt = f"{get_system_prompt()}\n\n以下のテキストをターゲット言語に意訳してください:\n\n{input_text}"
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.session_state.m2_result = res.text
                    st.success("意訳完了！")
            except Exception as e:
                st.error(f"エラー: {e}")

    if st.session_state.m2_result:
        st.markdown("### 📥 翻訳結果")
        fmt2 = st.radio("形式を選択", ["🎬 SRT字幕 (.srt)", "📄 プレーンテキスト (.txt)", "📦 両方"], key="m2_fmt")
        res_m2 = st.session_state.m2_result
        if "-->" in res_m2:
            m2_srt = res_m2
            m2_txt = srt_to_plain_text(res_m2)
        else:
            m2_txt = res_m2
            m2_srt = plain_text_to_srt(res_m2)

        if fmt2 == "🎬 SRT字幕 (.srt)":
            st.download_button("💾 SRT保存", data=m2_srt, file_name="script_localized.srt", mime="text/plain")
        elif fmt2 == "📄 プレーンテキスト (.txt)":
            st.download_button("💾 TXT保存", data=m2_txt, file_name="script_localized.txt", mime="text/plain")
        else:
            ca, cb = st.columns(2)
            with ca:
                st.download_button("💾 SRT保存", data=m2_srt, file_name="script_localized.srt", mime="text/plain", use_container_width=True)
            with cb:
                st.download_button("💾 TXT保存", data=m2_txt, file_name="script_localized.txt", mime="text/plain", use_container_width=True)
        
        st.text_area("翻訳内容", value=res_m2, height=300)

# ----------------------------------------------------
# TAB 3: 1文クイック提案 (FREEプラン解放)
# ----------------------------------------------------
with tab3:
    st.markdown("#### ⚡ 1文クイック提案（無料辞書モード）")
    phrase = st.text_input("ネイティブ表現を知りたいフレーズ", placeholder="例: マジでやばい、調子乗るなよ、What are you up to?")
    if st.button("💡 3パターン同時提案", use_container_width=True):
        if not st.session_state.gemini_api_key:
            st.error("左サイドバーに Gemini API Key を入力してください。")
        elif not phrase:
            st.warning("フレーズを入力してください。")
        else:
            try:
                with st.spinner("提案生成中..."):
                    client = genai.Client(api_key=st.session_state.gemini_api_key)
                    prompt = f"{get_system_prompt()}\n\n次のフレーズについて、「若者スラング」「サムネ用短縮表現」「日常会話」の3パターンとニュアンス解説を出力してください: 『{phrase}』"
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.markdown(res.text)
            except Exception as e:
                st.error(f"エラー: {e}")
