"""
YouTube Pro Video & Subtitle AI Translator
動画・音声ファイル（mp4, mp3, wav等）を直接アップロードして、
自動で文字起こし（タイムコード付きSRT生成）＋高精度ローカライズ翻訳を一括実行するStreamlitアプリ
"""

import streamlit as st
import anthropic
import openai
import os
import tempfile
import io

st.set_page_config(
    page_title="YouTube Pro Video AI Translator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ システム設定")
    
    st.info("💡 動画の音声認識にはOpenAI Whisperを使用し、翻訳・ローカライズにはClaudeまたはGPT-4oを使用します。")
    
    openai_key = st.text_input("OpenAI API Key (音声文字起こし用)", type="password", placeholder="sk-...")
    
    engine = st.selectbox(
        "翻訳AIエンジン",
        ["Claude (Anthropic)", "ChatGPT (OpenAI)"]
    )
    
    if engine == "Claude (Anthropic)":
        claude_key = st.text_input("Anthropic API Key (翻訳用)", type="password", placeholder="sk-ant-...")
        model_name = "claude-3-5-sonnet-20241022"
    else:
        claude_key = ""
        model_name = "gpt-4o"
        
    st.divider()
    st.header("🌐 翻訳設定")
    
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "英語 (US - 自然な日常会話)",
            "英語 (UK - イギリス英語)",
            "韓国語 (自然な敬語/パンマル)",
            "繁体字中国語 (台湾/香港向け)",
            "簡体字中国語",
            "スペイン語",
            "フランス語",
            "ドイツ語"
        ]
    )
    
    content_tone = st.selectbox(
        "動画ジャンル・口調",
        [
            "YouTubeエンタメ・実況（軽快・スラング適応）",
            "ビジネス・解説・教養（論理的・明瞭・丁寧）",
            "ストーリー・怪談・朗読（情緒的・ドラマチック）",
            "ショート動画（インパクト重視・短縮字幕）"
        ]
    )

    custom_instructions = st.text_area(
        "追加指示（任意）",
        placeholder="例: 主人公はフランクな口調に。専門用語「○○」はそのままにして。"
    )

def extract_srt_from_audio(file_bytes, file_ext, key):
    client = openai.OpenAI(api_key=key)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt"
            )
        return transcript
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def create_system_prompt(lang, tone, instructions):
    return f"""あなたはYouTube動画・字幕ローカライズの最高峰プロ翻訳者です。
【目的】
入力されたSRT字幕データを「{lang}」へ最高品質で翻訳・ローカライズしてください。

【重要ルール】
1. **文脈の最適化（意訳と自然さ）**: 動画ジャンル「{tone}」に適した、ネイティブYouTuberが使う最も自然な表現を採用してください。
2. **SRT形式の厳格な維持**: 番号とタイムコード（00:00:00,000 --> 00:00:00,000）は1文字も改変せず、字幕テキスト部分のみを翻訳して置き換えてください。
3. **可読性**: 視聴者が動画再生中に無理なく読めるよう、簡潔かつテンポの良い言葉選びを行ってください。
4. **個別指示**: {instructions if instructions else "なし"}
"""

def translate_srt(srt_text, sys_prompt, engine_type, openai_k, claude_k, model):
    if engine_type == "Claude (Anthropic)":
        client = anthropic.Anthropic(api_key=claude_k)
        res = client.messages.create(
            model=model,
            max_tokens=4096,
            system=sys_prompt,
            messages=[{"role": "user", "content": f"以下のSRT字幕をフォーマットを完全に維持して翻訳してください:\n\n{srt_text}"}],
            temperature=0.3
        )
        return res.content[0].text
    else:
        client = openai.OpenAI(api_key=openai_k)
        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"以下のSRT字幕をフォーマットを完全に維持して翻訳してください:\n\n{srt_text}"}
            ],
            temperature=0.3
        )
        return res.choices[0].message.content

# メインUI
st.markdown('<div class="main-header">🎬 YouTube Pro 動画直接アップロード AI翻訳ツール</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">動画（MP4等）や音声を入れるだけで、自動文字起こし＋タイムコード付き翻訳字幕（SRT）を一括生成します。</div>', unsafe_allow_html=True)

uploaded_media = st.file_uploader(
    "🎥 動画または音声ファイルをアップロード (.mp4, .mov, .mp3, .wav, .m4a)",
    type=["mp4", "mov", "mp3", "wav", "m4a"]
)

start_video_process = st.button("🚀 動画から直接翻訳字幕を一括生成", type="primary")

if start_video_process:
    if not openai_key:
        st.error("⚠️ 音声認識を行うため、サイドバーに「OpenAI API Key」を入力してください。")
    elif engine == "Claude (Anthropic)" and not claude_key:
        st.error("⚠️ 翻訳用エンジンにClaudeを選択しているため、「Anthropic API Key」を入力してください。")
    elif uploaded_media is None:
        st.warning("⚠️ 動画または音声ファイルをアップロードしてください。")
    else:
        with st.status("🎬 動画処理と翻訳を実行中...", expanded=True) as status:
            file_bytes = uploaded_media.getvalue()
            _, file_ext = os.path.splitext(uploaded_media.name)
            
            st.write("🎙️ 1/2 動画の音声を高精度文字起こし中 (Whisper)...")
            try:
                raw_srt = extract_srt_from_audio(file_bytes, file_ext, openai_key)
                st.write("🌐 2/2 ネイティブ向けに文脈ローカライズ翻訳中...")
                
                sys_prompt = create_system_prompt(target_lang, content_tone, custom_instructions)
                final_translated_srt = translate_srt(
                    raw_srt, sys_prompt, engine, openai_key, claude_key, model_name
                )
                
                status.update(label="✅ 全自動処理が完了しました！", state="complete", expanded=False)
                
                st.subheader("📤 生成された翻訳字幕 (SRT)")
                st.text_area("翻訳SRTデータ", value=final_translated_srt, height=300)
                
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        label="💾 翻訳後字幕をDL (.srt)",
                        data=final_translated_srt,
                        file_name=f"translated_{uploaded_media.name}.srt",
                        mime="text/plain"
                    )
                with col_dl2:
                    st.download_button(
                        label="📄 原文（日本語）字幕をDL (.srt)",
                        data=raw_srt,
                        file_name=f"original_{uploaded_media.name}.srt",
                        mime="text/plain"
                    )
                st.toast("🎉 字幕の作成と翻訳が完了しました！", icon="🚀")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
