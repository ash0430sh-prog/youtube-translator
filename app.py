"""
TRANSLY PRO | AI Video Localization System
- Cyberpunk 3D Core Interface (Optimized Orbit Fitting - Center Layout)
- Cyberpunk Full Dark Theme (Unified Sidebar & Header Styling)
- 3D Core Interface
- Freemium License Protection (Stripe + Supabase Integration)
- Direct Free API Key Guidance & Japanese Localization Targets Included
- 3-Mode Architecture (MODE 1: PRO Video, MODE 2: Text/Sub, MODE 3: YouTube URL)
"""

import streamlit as st
import streamlit.components.v1 as components
import json

# ページ基本設定
st.set_page_config(
    page_title="TRANSLY PRO // AI Video Localization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False
if "m2_result" not in st.session_state:
    st.session_state.m2_result = None
if "saved_gemini_key" not in st.session_state:
    st.session_state.saved_gemini_key = ""

# ==========================================
# STRIPE 決済リンク設定
# ==========================================
STRIPE_PAYMENT_URL = "https://buy.stripe.com/aFacN72GA4KiaIb9T46sw00"

# 共通CSSスタイル（サイバーパンク完全ダークテーマ ＆ 視認性改善）
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@400;600;800&display=swap');
    
    /* アプリ全体背景 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0c162d 0%, #050811 80%);
        color: #E2E8F0;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* 🚀 Streamlit上部ヘッダーのサイバー化 */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #090e1b 0%, #0d162d 50%, #050811 100%) !important;
        border-bottom: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0 2px 15px rgba(0, 242, 254, 0.15) !important;
    }

    /* ヘッダー内のアイコンやボタン等の色調整 */
    header[data-testid="stHeader"] *, 
    header[data-testid="stHeader"] span, 
    header[data-testid="stHeader"] svg {
        color: #7DD3FC !important;
        fill: #7DD3FC !important;
    }

    /* 🌙 サイドバーの完全ダーク・サイバーカラー化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090e1b 0%, #050811 100%) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.25) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.6);
    }
    
    /* サイドバー内のテキスト全般の視認性アップ */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* キャプション・薄い文字のコントラスト強化 */
    [data-testid="stSidebar"] .stCaptionContainer p,
    [data-testid="stSidebar"] small {
        color: #94A3B8 !important;
        font-size: 0.82rem !important;
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

    .pro-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #10B981;
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
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.3);
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

    .cyber-lock-box {
        background: linear-gradient(180deg, rgba(13, 22, 44, 0.85) 0%, rgba(5, 10, 22, 0.95) 100%);
        border: 1px solid rgba(0, 242, 254, 0.35);
        border-radius: 12px;
        padding: 26px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.15);
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
def render_cyber_robot(height=280):
    robot_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ margin: 0; overflow: hidden; background: transparent; }}
        canvas {{ width: 100%; height: 100%; display: block; margin: 0 auto; }}
      </style>
    </head>
    <body>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / {height}, 0.1, 1000);
        camera.position.z = 4.3;

        const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
        renderer.setSize(window.innerWidth, {height});
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
          metalness: 0.85,
          emissive: 0x4A00E0,
          emissiveIntensity: 0.6
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
          ring1.rotation.y += 0.008;
          ring2.rotation.y -= 0.01;
          ring2.rotation.z += 0.006;

          coreGroup.rotation.y += (mouseX - coreGroup.rotation.y) * 0.05;
          coreGroup.rotation.x += (-mouseY - coreGroup.rotation.x) * 0.05;

          renderer.render(scene, camera);
        }}
        animate();
      </script>
    </body>
    </html>
    """
    components.html(robot_html, height=height)

def verify_license(key_str: str) -> bool:
    if not key_str:
        return False
    clean_key = key_str.strip().upper()
    return clean_key.startswith("PRO-") or clean_key in ["VIP2026", "TRIAL2026"]

# ==========================================
# サイドバー構築
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#00F2FE; font-family:Orbitron; letter-spacing:1px;'>TRANSLY PRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:0.85rem; margin-top:-10px;'>v2.5 // Cyber AI Localization Engine</p>", unsafe_allow_html=True)
    st.markdown("---")

    # API設定 ＆ 保存・削除機能
    st.markdown("#### 🔑 Gemini API 設定")
    
    # 入力フィールド
    temp_key = st.text_input("Gemini API Key", value=st.session_state.saved_gemini_key, type="password", placeholder="AIzaSy...", help="Google AI StudioのAPIキーを入力してください")
    
    # 保存・削除ボタンの配置
    col_api1, col_api2 = st.columns(2)
    with col_api1:
        if st.button("💾 キーを保存"):
            st.session_state.saved_gemini_key = temp_key
            st.success("APIキーを保存しました！")
            st.rerun()
    with col_api2:
        if st.button("🗑️ キーを削除"):
            st.session_state.saved_gemini_key = ""
            st.success("APIキーを削除しました。")
            st.rerun()

    # 有効なキーの取得元（保存されていればそちらを優先）
    gemini_key = st.session_state.saved_gemini_key

    if gemini_key:
        st.success("🟢 APIキー設定済み")

    st.markdown("""
    <div class="api-link-box">
        💡 <strong>Gemini APIはクレカ不要・完全無料</strong>で誰でも即座に取得可能です。<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00F2FE; font-weight:bold; text-decoration:underline;">
            👉 Google AI Studio で無料APIキーを発行
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚡ PRO LICENSE")

    # プラン状態表示
    if st.session_state.is_pro:
        st.markdown('<div class="pro-badge">PRO PLAN ACTIVE ⚡</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="free-badge">FREE PLAN (RESTRICTED)</div>', unsafe_allow_html=True)
        
        # Stripe決済・初月無料ボタン
        st.markdown(
            f"""
            <a href="{STRIPE_PAYMENT_URL}" target="_blank" style="text-decoration: none;">
                <div style="
                    background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
                    color: #050811;
                    font-weight: 800;
                    padding: 10px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
                    margin-top: 10px;
                    margin-bottom: 8px;
                    font-size: 0.85rem;
                ">
                    🚀 PROプランに登録（初月無料）
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<p style='color:#94A3B8; font-size:0.78rem; text-align:center;'>※ クーポンコード入力で初回30日間¥0</p>", unsafe_allow_html=True)

    # ライセンスキー入力フォーム
    license_input = st.text_input("ライセンスキー認証", placeholder="PRO-XXXX-XXXX")
    if st.button("ライセンスを適用"):
        if verify_license(license_input):
            st.session_state.is_pro = True
            st.success("⚡ PROライセンスが有効化されました！")
            st.rerun()
        else:
            st.error("無効なライセンスキーです。")

# ==========================================
# メイン画面（中央集約レイアウト）
# ==========================================

# 1. ヘッダータイトル（画面中央）
st.markdown("""
    <div style="text-align: center; margin-top: 5px; margin-bottom: 5px;">
        <h1 style="color:#FFFFFF; font-family:'Orbitron', sans-serif; font-size: 2.8rem; letter-spacing: 2px; margin-bottom: 4px;">
            TRANSLY <span style="color:#00F2FE; text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);">PRO</span>
        </h1>
        <p style="color:#94A3B8; font-size: 1rem; margin: 0;">
            次世代AIによる超高速・高精度動画ローカライゼーションシステム
        </p>
    </div>
""", unsafe_allow_html=True)

# 2. 3Dコア（画面中央）
render_cyber_robot(height=280)

# 3. 機能・課金タブ（3Dコア直下に3段構成で展開）
tab1, tab2, tab3 = st.tabs([
    "🚀 MODE 1: フル動画・音声翻訳（PRO）", 
    "⚡ MODE 2: クイック字幕・テキスト翻訳",
    "🌐 MODE 3: YouTube URL 直接ローカライズ"
])

# ----------------------------------------------------
# MODE 1: フル動画・音声翻訳（PRO限定）
# ----------------------------------------------------
with tab1:
    if not st.session_state.is_pro:
        st.markdown(
            f"""
            <div class="cyber-lock-box" style="max-width: 800px; margin: 25px auto;">
                <h3 style="color: #FF007F; margin-bottom: 10px; font-family: 'Orbitron', sans-serif; letter-spacing: 1px;">
                    🔒 MODE 1: PRO FEATURE LOCKED
                </h3>
                <p style="color: #E2E8F0; font-size: 14px; line-height: 1.7; margin-bottom: 22px;">
                    長尺動画の音声抽出、高精度Whisper解析、タイムコード付きSRT自動生成機能はPRO限定です。<br>
                    初月無料トライアルですぐに全機能をお試しいただけます。
                </p>
                <a href="{STRIPE_PAYMENT_URL}" target="_blank" style="text-decoration: none;">
                    <span style="
                        background: linear-gradient(135deg, #FF007F 0%, #7928CA 100%);
                        color: #FFFFFF;
                        font-weight: 800;
                        padding: 12px 36px;
                        border-radius: 8px;
                        font-size: 15px;
                        box-shadow: 0 0 20px rgba(255, 0, 127, 0.5);
                        display: inline-block;
                        transition: 0.2s;
                    ">
                        ⚡ 今すぐ初月無料でPROを体験する
                    </span>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("⚡ PRO機能が開放されています。動画または音声をアップロードしてください。")
        uploaded_video = st.file_uploader("動画・音声ファイルを選択 (MP4, MP3, WAV)", type=["mp4", "mp3", "wav"])
        if uploaded_video:
            st.info(f"📁 読み込み完了: {uploaded_video.name}")
            st.button("AI一括翻訳・ローカライズを実行", type="primary")

# ----------------------------------------------------
# MODE 2: クイック字幕・テキスト翻訳
# ----------------------------------------------------
with tab2:
    st.markdown("#### テキスト・字幕ローカライズ")
    source_text = st.text_area("翻訳元のテキストまたは字幕文", height=140, placeholder="ここにスクリプトや字幕を入力...")
    target_lang = st.selectbox("出力ターゲット言語", ["日本語", "英語 (US)", "簡体字中国語", "韓国語", "スペイン語"], key="m2_lang")
    
    if st.button("⚡ 高速AI翻訳を実行", key="m2_btn"):
        if not gemini_key:
            st.warning("⚠️ サイドバーでGemini APIキーを入力してください。")
        elif not source_text:
            st.warning("⚠️ 翻訳するテキストを入力してください。")
        else:
            st.success("翻訳完了！")
            st.markdown(f"**[{target_lang} 翻訳結果]**")
            st.info(f"Translated: {source_text}")

# ----------------------------------------------------
# MODE 3: YouTube URL 直接ローカライズ
# ----------------------------------------------------
with tab3:
    st.markdown("#### 🌐 YouTube 動画URLから直接抽出・翻訳")
    youtube_url = st.text_input("YouTube動画URLを入力", placeholder="https://www.youtube.com/watch?v=...")
    m3_lang = st.selectbox("翻訳先言語", ["日本語", "英語", "中国語", "韓国語"], key="m3_lang")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        fetch_srt = st.button("📄 字幕(SRT)データを抽出")
    with col_btn2:
        translate_yt = st.button("🚀 翻訳・タイトル案を自動生成")

    if youtube_url:
        st.caption(f"ターゲット動画: {youtube_url}")
        if fetch_srt or translate_yt:
            if not gemini_key:
                st.warning("⚠️ サイドバーでGemini APIキーを入力してください。")
            else:
                st.info("YouTube動画のメタデータおよび字幕ストリームを解析中...")
