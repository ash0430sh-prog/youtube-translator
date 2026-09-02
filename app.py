"""
TRANSLY PRO | AI Video Localization System
- Freemium License Protection (Supabase Integration)
- State-Preserving Multi-Format Translator (SRT/TXT)
- Full Auto-Healing Fallback Engine
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
    page_title="TRANSLY PRO | AI動画ローカライズ",
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

# 共通CSSスタイル
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Noto+Sans+JP:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #050811;
        color: #E2E8F0;
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    .pro-badge-active {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF;
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.08em;
        display: inline-block;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    
    .free-badge {
        background: rgba(148, 163, 184, 0.15);
        border: 1px solid rgba(148, 163, 184, 0.3);
        color: #94A3B8;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
    
    .lock-card {
        background: linear-gradient(135deg, rgba(13, 22, 44, 0.95) 0%, rgba(8, 15, 30, 0.98) 100%);
        border: 1px dashed rgba(0, 242, 254, 0.4);
        border-radius: 16px;
        padding: 36px 24px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
        margin: 20px 0;
    }
    .lock-icon {
        font-size: 3rem;
        margin-bottom: 12px;
        display: block;
    }
    .lock-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #00F2FE;
        margin-bottom: 10px;
    }
    .lock-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        max-width: 580px;
        margin: 0 auto 20px auto;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Supabaseによるライセンス検証
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

# サイドバー
with st.sidebar:
    st.markdown("### 👾 TRANSLY PRO")
    
    st.markdown("#### 💎 PRO 会員認証")
    input_license = st.text_input(
        "ライセンスキー (PRO会員用)",
        value=st.session_state.license_key,
        type="password",
        help="発行されたライセンスキーを入力してください"
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
        if st.button("ログアウト", use_container_width=True):
            st.session_state.license_key = ""
            st.session_state.is_pro_active = False
            st.rerun()

    if st.session_state.is_pro_active:
        st.markdown('<div class="pro-badge-active">PRO ACTIVE 🔓 全機能解放中</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="free-badge">FREE PLAN (MODE 2 & 3 利用可能)</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("#### 🔑 Gemini API Key (0円)")
    user_key = st.text_input("Google AI Studio Key", value=st.session_state.gemini_api_key, type="password")
    if user_key:
        st.session_state.gemini_api_key = user_key.strip()
    
    st.markdown("---")
    st.markdown("#### 🌐 翻訳設定")
    target_lang = st.selectbox(
        "翻訳先言語",
        ["英語 (US日常会話/スラング)", "英語 (ビジネス/丁寧)", "韓国語", "繁体字中国語 (台湾/香港)", "スペイン語"]
    )
    video_genre = st.selectbox(
        "動画ジャンル・世界観",
        ["⚡ ショート/リール/TikTok (短縮重視)", "🔥 YouTubeエンタメ・実況 (テンポ重視)", "📖 2ch/修羅場/スカッと系 (煽り重視)", "🎓 解説・ビジネス・教養"]
    )
    custom_rule = st.text_area("個別ルール・固有名詞 (任意)", placeholder="例: 専門用語の指定やスラングの調整")

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
- 直訳は厳禁。ネイティブがショート動画やYouTubeで自然に使う口語・スラングに翻訳すること。
- 字幕は1行あたり短く保ち、スマホ画面で一瞬で読めるテンポにすること。
"""

# メインコンテンツ
st.markdown("## ⚡ TRANSLY PRO — AI Video Localization")
st.markdown("<p style='color:#94A3B8;'>完全無料Google AIを活用し、Premiere / CapCut対応の字幕SRT・タイトル案を一発生成</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🎬 MODE 1: 動画・音声投入 (PRO)",
    "📋 MODE 2: 台本・SRTコピペ (FREE)",
    "⚡ MODE 3: 1文クイック提案 (FREE)"
])

with tab1:
    if not st.session_state.is_pro_active:
        st.markdown("""
        <div class="lock-card">
            <span class="lock-icon">🔒</span>
            <div class="lock-title">PRO PLAN EXCLUSIVE</div>
            <div class="lock-desc">
                動画・音声ファイル（MP4 / MOV / MP3）からの直接SRT生成・タイムコード完全同期機能は <strong>PRO会員限定</strong> です。<br>
                台本テキストの翻訳（MODE 2）や1文提案（MODE 3）は無料プランのまますぐにご利用いただけます。
            </div>
            <p style="color:#00F2FE; font-size:0.9rem; font-weight:700;">月額プラン加入後、サイドバーに発行されたライセンスキーを入力すると即時解放されます。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("#### 🎬 メディアファイルを直接ドロップ")
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

with tab2:
    st.markdown("#### 📋 台本テキスト / SRT字幕 コピペ翻訳（無料）")
    input_text = st.text_area("翻訳したい日本語台本またはSRT字幕を貼り付け", height=200)
    
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

with tab3:
    st.markdown("#### ⚡ 1文クイック提案（無料辞書モード）")
    phrase = st.text_input("ネイティブ表現を知りたい日本語フレーズ", placeholder="例: マジでやばい、調子乗るなよ")
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
