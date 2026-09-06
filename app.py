"""
TRANSLY PRO | AI Video Localization System (Clean Sidebar & UI Updated)
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import tempfile
import time
from datetime import datetime, timedelta

# ページ基本設定
st.set_page_config(
    page_title="TRANSLY PRO // AI Video Localization",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 永続化パラメータの管理
# ==========================================
query_params = st.query_params

if "is_pro" not in st.session_state:
  st.session_state.is_pro = False
if "pro_expiry_date" not in st.session_state:
  st.session_state.pro_expiry_date = None

is_url_pro = query_params.get("pro") == "true"
if is_url_pro:
  st.session_state.is_pro = True
  if not st.session_state.pro_expiry_date:
    st.session_state.pro_expiry_date = (
        datetime.now() + timedelta(days=30)
    ).strftime("%Y-%m-%d")

# ==========================================
# サブスク継続 / 有効期限のチェックロジック
# ==========================================
def check_subscription_status() -> bool:
  if not st.session_state.is_pro:
    return False

  if st.session_state.pro_expiry_date:
    expiry = datetime.strptime(st.session_state.pro_expiry_date, "%Y-%m-%d")
    if datetime.now() > expiry:
      st.session_state.is_pro = False
      return False

  subscription_active = True
  if not subscription_active:
    st.session_state.is_pro = False
    return False

  return True


st.session_state.is_pro = check_subscription_status()

url_api_key = query_params.get("api_key", "")
if "saved_gemini_key" not in st.session_state:
  st.session_state.saved_gemini_key = url_api_key
elif url_api_key and not st.session_state.saved_gemini_key:
  st.session_state.saved_gemini_key = url_api_key

if "m2_result" not in st.session_state:
  st.session_state.m2_result = None

STRIPE_PAYMENT_URL = "https://buy.stripe.com/aFacN72GA4KiaIb9T46sw00"

# 共通CSSスタイル
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&family=Noto+Sans+JP:wght@400;600;800&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0c162d 0%, #050811 80%);
        color: #E2E8F0;
        font-family: 'Noto Sans JP', sans-serif;
    }

    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #090e1b 0%, #0d162d 50%, #050811 100%) !important;
        border-bottom: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0 2px 15px rgba(0, 242, 254, 0.15) !important;
    }

    header[data-testid="stHeader"] *, 
    header[data-testid="stHeader"] span, 
    header[data-testid="stHeader"] svg {
        color: #7DD3FC !important;
        fill: #7DD3FC !important;
    }

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

    [data-testid="stSidebar"] .stCaptionContainer p,
    [data-testid="stSidebar"] small {
        color: #94A3B8 !important;
        font-size: 0.82rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(0, 242, 254, 0.18) !important;
    }

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
    
    .cyber-card {
        background: linear-gradient(135deg, rgba(13, 22, 44, 0.9) 0%, rgba(10, 15, 30, 0.95) 100%);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.08);
    }

    div.stRadio label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
    }
    
    div.stCheckbox label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
        padding-top: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def render_cyber_robot(height=260):
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
# 自動リカバリー関数
# ==========================================
def call_gemini_with_auto_retry(client, contents_data):
  models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

  for model_name in models_to_try:
    for attempt in range(2):
      try:
        response = client.models.generate_content(
            model=model_name, contents=contents_data
        )
        return response
      except Exception as e:
        err_str = str(e)
        if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str:
          time.sleep(2)
          continue
        elif "404" in err_str or "NOT_FOUND" in err_str:
          break
        else:
          raise e
  raise Exception(
      "サーバーが非常に混雑しています。少し時間を置いてから再度実行してください。"
  )


# ==========================================
# サイドバー構築
# ==========================================
with st.sidebar:
  st.markdown(
      "<h2"
      " style='color:#00F2FE; font-family:Orbitron;"
      " letter-spacing:1px;'>TRANSLY PRO</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color:#94A3B8; font-size:0.85rem; margin-top:-10px;'>v2.5 //"
      " Cyber AI Localization Engine</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")

  st.markdown("#### 🔑 Gemini API 設定")
  temp_key = st.text_input(
      "Gemini API Key (AQ...)",
      value=st.session_state.saved_gemini_key,
      type="password",
      placeholder="AQ...",
      help="Google AI Studioで取得したAPIキーを入力してください",
  )

  col_api1, col_api2 = st.columns(2)
  with col_api1:
    if st.button("💾 キーを保存"):
      st.session_state.saved_gemini_key = temp_key
      st.query_params["api_key"] = temp_key
      st.success("APIキーを保存しました！")
      st.rerun()
  with col_api2:
    if st.button("🗑️ キーを削除"):
      st.session_state.saved_gemini_key = ""
      if "api_key" in st.query_params:
        del st.query_params["api_key"]
      st.success("APIキーを削除しました。")
      st.rerun()

  gemini_key = st.session_state.saved_gemini_key

  if gemini_key:
    st.success("🟢 APIキー設定済み")

  st.markdown(
      """
    <div class="api-link-box">
        💡 <strong>Google AI Studio</strong> のAPIキーに対応しています。<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00F2FE; font-weight:bold; text-decoration:underline;">
            👉 Google AI Studio でキー管理
        </a>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("---")
  st.markdown("#### ⚡ PRO LICENSE")

  if st.session_state.is_pro:
    st.markdown(
        '<div class="pro-badge">PRO PLAN ACTIVE ⚡</div>', unsafe_allow_html=True
    )
    if st.session_state.pro_expiry_date:
      # 有効期限の文字色を明るく見やすくハイライト
      st.markdown(
          f"<p"
          f" style='color:#00F2FE; font-size:0.85rem; text-align:center;"
          f" margin-top:6px; font-weight:600;'>📅 有効期限:"
          f" {st.session_state.pro_expiry_date} まで</p>",
          unsafe_allow_html=True,
      )
  else:
    st.markdown(
        '<div class="free-badge">FREE PLAN (RESTRICTED)</div>',
        unsafe_allow_html=True,
    )

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
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#94A3B8; font-size:0.78rem; text-align:center;'>※"
        " 初回30日間¥0で全機能使い放題</p>",
        unsafe_allow_html=True,
    )

  license_input = st.text_input(
      "ライセンスキー認証",
      value="",
      placeholder="VIP2026 または PRO-...",
  )
  if st.button("ライセンスを適用"):
    if verify_license(license_input):
      st.session_state.is_pro = True
      st.session_state.pro_expiry_date = (
          datetime.now() + timedelta(days=30)
      ).strftime("%Y-%m-%d")
      st.query_params["pro"] = "true"
      st.success("⚡ PROライセンス（30日間）が有効化されました！")
      st.rerun()
    else:
      st.error("無効なライセンスキーです。")

# ==========================================
# メイン画面
# ==========================================

st.markdown(
    """
    <div style="text-align: center; margin-top: 5px; margin-bottom: 5px;">
        <h1 style="color:#FFFFFF; font-family:'Orbitron', sans-serif; font-size: 2.6rem; letter-spacing: 2px; margin-bottom: 4px;">
            TRANSLY <span style="color:#00F2FE; text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);">PRO</span>
        </h1>
        <p style="color:#94A3B8; font-size: 0.95rem; margin: 0;">
            次世代AIによる超高速・高精度動画ローカライゼーションシステム
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

render_cyber_robot(height=240)

# 機能タブ
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 MODE 1: フル動画・音声翻訳（PRO）",
    "⚡ MODE 2: クイック字幕・テキスト翻訳",
    "🌐 MODE 3: YouTube URL 直接ローカライズ",
    "📖 使い方ガイド ＆ 料金プラン",
])

# MODE 1
with tab1:
  if not st.session_state.is_pro:
    st.markdown(
        f"""
            <div class="cyber-lock-box" style="max-width: 800px; margin: 20px auto;">
                <h3 style="color: #FF007F; margin-bottom: 10px; font-family: 'Orbitron', sans-serif; letter-spacing: 1px;">
                    🔒 MODE 1: PRO FEATURE LOCKED
                </h3>
                <p style="color: #E2E8F0; font-size: 14px; line-height: 1.7; margin-bottom: 22px;">
                    長尺動画の音声抽出、高精度解析、タイムコード付きSRT自動生成機能はPRO限定です。<br>
                    初月無料トライアル期間の終了、または毎月の決済未確認によりロックされています。
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
                        ⚡ 有料プランを継続 / 再開する
                    </span>
                </a>
            </div>
            """,
        unsafe_allow_html=True,
    )
  else:
    st.success(
        "⚡ PRO機能が有効化されています。動画または音声をアップロードしてください。"
    )
    uploaded_video = st.file_uploader(
        "動画・音声ファイルを選択 (MP4, MP3, WAV)", type=["mp4", "mp3", "wav"]
    )

    if uploaded_video:
      st.info(f"📁 読み込み完了: {uploaded_video.name}")

      st.markdown(
          "<div class='cyber-card'>"
          "<p"
          " style='color:#00F2FE; font-family:Orbitron; font-weight:bold;"
          " font-size:1.1rem; margin-bottom:15px;'>⚙️ CONFIG //"
          " 翻訳・出力設定</p>",
          unsafe_allow_html=True,
      )

      col_opt1, col_opt2 = st.columns([1, 1], gap="large")
      with col_opt1:
        m1_lang = st.selectbox(
            "ターゲット出力言語",
            ["日本語", "英語 (US)", "簡体字中国語", "韓国語"],
            key="m1_lang",
        )
        output_format_1 = st.radio(
            "📄 出力形式を選択",
            [
                "通常のテキスト版（文字起こし＋翻訳）",
                "タイムコード付き字幕テキスト（SRT形式風）",
            ],
            key="m1_format",
        )

      with col_opt2:
        st.markdown(
            "<div style='height: 32px;'></div>", unsafe_allow_html=True
        )
        include_summary_1 = st.checkbox(
            "📊 動画の要約とSNS用タイトル案を合わせて出力する",
            value=True,
            key="m1_summary",
        )

      st.markdown("</div>", unsafe_allow_html=True)

      if st.button("🚀 AI一括翻訳・ローカライズを実行", type="primary"):
        if not gemini_key:
          st.warning("⚠️ サイドバーでGemini APIキーを入力してください。")
        else:
          try:
            from google import genai

            client = genai.Client(api_key=gemini_key)

            with st.spinner(
                "🤖 Gemini AIが自動リカバリー機能を使って解析・翻訳中..."
            ):
              with tempfile.NamedTemporaryFile(
                  delete=False, suffix="." + uploaded_video.name.split(".")[-1]
              ) as tmp_file:
                tmp_file.write(uploaded_video.getvalue())
                tmp_path = tmp_file.name

              video_file = client.files.upload(file=tmp_path)

              while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = client.files.get(name=video_file.name)

              format_instruction = (
                  "タイムコード付きの字幕テキスト（SRT形式風、例: [00:00 - 00:05] セリフ...）として出力してください。"
                  if "SRT" in output_format_1
                  else "読みやすい通常のテキスト形式（話者ごとの文字起こしと自然な翻訳）で出力してください。"
              )

              summary_instruction = (
                  "さらに、動画の要約とSNS用タイトル案も合わせて出力してください。"
                  if include_summary_1
                  else "※要約およびタイトル案の出力は不要です。"
              )

              prompt = f"""
                            この動画（または音声）の音声を詳細に文字起こしし、自然な {m1_lang} に翻訳してください。
                            
                            【出力形式の指定】
                            {format_instruction}
                            
                            【追加情報の指定】
                            {summary_instruction}
                            """

              response = call_gemini_with_auto_retry(
                  client, [video_file, prompt]
              )

              st.success("🎉 ローカライズ・翻訳処理が完了しました！")
              st.markdown("### 📝 翻訳・字幕出力結果")
              st.markdown(response.text)

              file_ext = "srt" if "SRT" in output_format_1 else "txt"
              st.download_button(
                  label=f"💾 結果をファイル（.{file_ext}）でダウンロード",
                  data=response.text,
                  file_name=f"transly_result.{file_ext}",
                  mime="text/plain",
              )

          except Exception as e:
            st.error(
                f"エラーが発生しました（自動リカバリー上限に達しました）: {e}"
            )

# MODE 2
with tab2:
  st.markdown("#### テキスト・字幕ローカライズ")
  source_text = st.text_area(
      "翻訳元のテキストまたは字幕文",
      height=140,
      placeholder="ここにスクリプトや字幕を入力...",
  )

  st.markdown(
      "<div class='cyber-card'>"
      "<p"
      " style='color:#00F2FE; font-family:Orbitron; font-weight:bold;"
      " font-size:1.1rem; margin-bottom:15px;'>⚙️ CONFIG //"
      " 翻訳・出力設定</p>",
      unsafe_allow_html=True,
  )

  col_m2_1, col_m2_2 = st.columns([1, 1], gap="large")
  with col_m2_1:
    target_lang = st.selectbox(
        "出力ターゲット言語",
        ["日本語", "英語 (US)", "簡体字中国語", "韓国語", "スペイン語"],
        key="m2_lang",
    )
    output_format_2 = st.radio(
        "📄 出力形式を選択",
        [
            "通常のテキスト版（翻訳文のみ）",
            "タイムコード付き字幕テキスト（SRT形式風）",
        ],
        key="m2_format",
    )

  with col_m2_2:
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    include_summary_2 = st.checkbox(
        "📊 テキストの要約とタイトル案を合わせて出力する",
        value=False,
        key="m2_summary",
    )

  st.markdown("</div>", unsafe_allow_html=True)

  if st.button("⚡ 高速AI翻訳を実行", key="m2_btn"):
    if not gemini_key:
      st.warning("⚠️ サイドバーでGemini APIキーを入力してください。")
    elif not source_text:
      st.warning("⚠️ 翻訳するテキストを入力してください。")
    else:
      try:
        from google import genai

        client = genai.Client(api_key=gemini_key)

        format_inst_2 = (
            "タイムコード付きの字幕テキスト（SRT形式風）として出力してください。"
            if "SRT" in output_format_2
            else "通常の読みやすいテキスト形式で出力してください。"
        )
        summary_inst_2 = (
            "さらに、テキストの要約とタイトル案も合わせて出力してください。"
            if include_summary_2
            else ""
        )

        prompt = f"""
                以下のテキストを自然な {target_lang} に翻訳してください。
                
                【出力形式の指定】
                {format_inst_2}
                
                {summary_inst_2}
                
                ---
                {source_text}
                """

        with st.spinner("🤖 Gemini AIが自動リカバリー機能を使って翻訳中..."):
          response = call_gemini_with_auto_retry(client, prompt)
          st.success("翻訳完了！")
          st.markdown(f"**[{target_lang} 翻訳結果]**")
          st.markdown(response.text)

          file_ext_2 = "srt" if "SRT" in output_format_2 else "txt"
          st.download_button(
              label=f"💾 翻訳結果をダウンロード（.{file_ext_2}）",
              data=response.text,
              file_name=f"transly_text_result.{file_ext_2}",
              mime="text/plain",
          )
      except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# MODE 3
with tab3:
  st.markdown("#### 🌐 YouTube 動画URLから直接抽出・翻訳")
  youtube_url = st.text_input(
      "YouTube動画URLを入力",
      placeholder="https://www.youtube.com/watch?v=...",
  )

  st.markdown(
      "<div class='cyber-card'>"
      "<p"
      " style='color:#00F2FE; font-family:Orbitron; font-weight:bold;"
      " font-size:1.1rem; margin-bottom:15px;'>⚙️ CONFIG //"
      " 翻訳・出力設定</p>",
      unsafe_allow_html=True,
  )

  col_m3_1, col_m3_2 = st.columns([1, 1], gap="large")
  with col_m3_1:
    m3_lang = st.selectbox(
        "翻訳先言語", ["日本語", "英語", "中国語", "韓国語"], key="m3_lang"
    )
    output_format_3 = st.radio(
        "📄 出力形式を選択",
        [
            "通常のテキスト版（字幕抽出＋翻訳）",
            "タイムコード付き字幕テキスト（SRT形式風）",
        ],
        key="m3_format",
    )

  with col_m3_2:
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    include_summary_3 = st.checkbox(
        "📊 動画の要約とSNS用タイトル案を合わせて出力する",
        value=True,
        key="m3_summary",
    )

  st.markdown("</div>", unsafe_allow_html=True)

  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    fetch_srt = st.button("📄 字幕データを抽出・翻訳")
  with col_btn2:
    translate_yt = st.button("🚀 フル解析・タイトル案を自動生成")

  if youtube_url and (fetch_srt or translate_yt):
    if not gemini_key:
      st.warning("⚠️ サイドバーでGemini APIキーを入力してください。")
    else:
      try:
        from google import genai

        client = genai.Client(api_key=gemini_key)
        format_inst_3 = (
            "タイムコード付きの字幕テキスト（SRT形式風）として出力してください。"
            if "SRT" in output_format_3
            else "通常のテキスト形式で出力してください。"
        )
        summary_inst_3 = (
            "さらに、動画の要約とSNS用タイトル案も合わせて出力してください。"
            if include_summary_3
            else ""
        )

        with st.spinner("🌐 YouTube動画データおよび音声を解析・翻訳中..."):
          prompt = f"""
                    YouTube URL: {youtube_url}
                    この動画の音声または公開字幕データを基に、自然な {m3_lang} にローカライズしてください。
                    
                    【出力形式の指定】
                    {format_inst_3}
                    
                    {summary_inst_3}
                    """
          response = call_gemini_with_auto_retry(client, prompt)

          st.success("🎉 YouTube動画のローカライズが完了しました！")
          st.markdown(response.text)

          file_ext_3 = "srt" if "SRT" in output_format_3 else "txt"
          st.download_button(
              label=f"💾 結果をダウンロード（.{file_ext_3}）",
              data=response.text,
              file_name=f"youtube_transly.{file_ext_3}",
              mime="text/plain",
          )
      except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# 📖 使い方ガイド ＆ 料金プラン
with tab4:
  st.markdown("### 📖 TRANSLY PRO ご利用ガイド & 料金プラン")

  st.markdown(
      """
    <div style="
        display: flex; 
        gap: 15px; 
        background: rgba(13, 22, 44, 0.85); 
        border: 1px solid rgba(0, 242, 254, 0.35); 
        border-radius: 12px; 
        padding: 25px; 
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.1);
    ">
        <div style="flex: 1; border-right: 1px solid rgba(0, 242, 254, 0.2); padding-right: 15px;">
            <h4 style="color: #00F2FE; font-family: Orbitron; margin-top:0;">STEP 01</h4>
            <p style="font-weight: bold; color: #FFFFFF; margin-bottom: 6px;">Gemini APIキー設定</p>
            <p style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                Google AI StudioからAPIキーを取得し、サイドバーに入力・保存します。
            </p>
        </div>
        <div style="flex: 1; border-right: 1px solid rgba(0, 242, 254, 0.2); padding-right: 15px; padding-left: 5px;">
            <h4 style="color: #00F2FE; font-family: Orbitron; margin-top:0;">STEP 02</h4>
            <p style="font-weight: bold; color: #FFFFFF; margin-bottom: 6px;">モードを選ぶ・出力設定</p>
            <p style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                テキスト形式やSRT形式、要約の有無を好みに合わせて選択して実行します。
            </p>
        </div>
        <div style="flex: 1; padding-left: 5px;">
            <h4 style="color: #FF007F; font-family: Orbitron; margin-top:0;">STEP 03</h4>
            <p style="font-weight: bold; color: #FFFFFF; margin-bottom: 6px;">自動リカバリー & 期限管理</p>
            <p style="font-size: 0.82rem; color: #94A3B8; line-height: 1.5;">
                混雑エラーは自動再試行。トライアル期限や毎月の決済未確認時は自動でロックされます。
            </p>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("---")

  price_col1, price_col2 = st.columns(2)

  with price_col1:
    st.markdown(
        """
            <div style="background: rgba(13, 22, 44, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 22px; text-align: center;">
                <h4 style="color: #94A3B8; margin-bottom: 5px;">FREE PLAN</h4>
                <h2 style="color: #FFFFFF; font-size: 1.8rem; margin: 10px 0;">0円 <span style="font-size: 0.9rem; font-weight: normal; color: #94A3B8;">/ ずっと無料</span></h2>
                <hr style="border-color: rgba(148, 163, 184, 0.2); margin: 15px 0;">
                <p style="font-size: 0.88rem; color: #CBD5E1; text-align: left; line-height: 1.6;">
                    ✅ MODE 2（テキスト翻訳）利用可能<br>
                    ✅ MODE 3（YouTube URL解析）利用可能<br>
                    ❌ フル動画・音声抽出（MODE 1）はロック
                </p>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with price_col2:
    st.markdown(
        f"""
            <div style="background: linear-gradient(135deg, rgba(13, 22, 44, 0.9) 0%, rgba(20, 10, 35, 0.95) 100%); border: 2px solid #FF007F; border-radius: 10px; padding: 22px; text-align: center; box-shadow: 0 0 20px rgba(255, 0, 127, 0.25);">
                <h4 style="color: #FF007F; margin-bottom: 5px; font-family: Orbitron;">⚡ TRANSLY PRO</h4>
                <h2 style="color: #FFFFFF; font-size: 1.8rem; margin: 10px 0;">1,500円 <span style="font-size: 0.9rem; font-weight: normal; color: #94A3B8;">/ 月 (税別)</span></h2>
                <p style="color: #00F2FE; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px;">🎉 初回30日間は完全無料でお試し可能！</p>
                <hr style="border-color: rgba(255, 0, 127, 0.3); margin: 15px 0;">
                <p style="font-size: 0.88rem; color: #CBD5E1; text-align: left; line-height: 1.6;">
                    🔥 MODE 1（長尺動画・音声一括翻訳）が無制限<br>
                    🔥 高精度解析 & SRT自動生成<br>
                    🔥 クレカ / Apple Pay / Google Pay 対応
                </p>
                <a href="{STRIPE_PAYMENT_URL}" target="_blank" style="text-decoration: none; display: block; margin-top: 15px;">
                    <span style="
                        background: linear-gradient(135deg, #FF007F 0%, #7928CA 100%);
                        color: #FFFFFF;
                        font-weight: 800;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-size: 0.9rem;
                        box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
                        display: block;
                    ">
                        🚀 初月無料でPROプランに登録
                    </span>
                </a>
            </div>
            """,
        unsafe_allow_html=True,
    )
