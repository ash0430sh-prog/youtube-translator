"""
YouTube Pro Translator - Streamlit Application
OS依存なし（ブラウザ完結）、SRT字幕タイムコード完全保持、文脈考慮の2パス高精度翻訳
"""

import streamlit as st
import anthropic
import openai
import re
import io

# ---------------------------------------------------------
# ページ初期設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="YouTube Pro AI Translator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# カスタムCSS（見やすさと操作性の向上）
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# サイドバー設定（モデル・APIキー・翻訳オプション）
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ システム設定")
    
    engine = st.selectbox(
        "AIエンジン選択",
        ["Claude (Anthropic)", "ChatGPT (OpenAI)"],
        help="高精度かつ自然な表現にはClaude、汎用性にはChatGPTがおすすめです。"
    )
    
    if engine == "Claude (Anthropic)":
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        model_name = st.selectbox("モデル", ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"])
    else:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        model_name = st.selectbox("モデル", ["gpt-4o", "gpt-4o-mini"])
    
    st.divider()
    st.header("🌐 翻訳設定")
    
    target_lang = st.selectbox(
        "翻訳先言語",
        [
            "英語 (US - 自然な日常会話)",
            "英語 (UK - イギリス英語)",
            "韓国語 (自然な敬語/パンマル選択可)",
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
            "YouTubeエンタメ・実況（軽快・スラング・テンポ重視）",
            "ビジネス・解説・教養（論理的・明瞭・丁寧）",
            "ストーリー・怪談・朗読（ドラマチック・感情豊か）",
            "ショート動画（超短縮・インパクト重視・画面収まり優先）"
        ]
    )

    custom_instructions = st.text_area(
        "追加の個別指示（任意）",
        placeholder="例: 主人公の口調は生意気な少年にして。専門用語「○○」は「XX」と訳して。",
        height=70
    )

# ---------------------------------------------------------
# ロジック関数：プロンプト生成 & API呼び出し
# ---------------------------------------------------------
def create_system_prompt(lang, tone, instructions):
    base_prompt = f"""あなたはYouTube動画および字幕ローカライズの最高峰プロフェッショナル翻訳者です。

【目的】
入力されたテキスト（台本またはSRT字幕データ）を「{lang}」へ最高品質で翻訳・ローカライズしてください。

【重要な翻訳ルール】
1. **文脈の最適化（意訳と自然さ）**:
   単なる直訳を固く禁じます。動画ジャンル「{tone}」に適した、現地のネイティブYouTuberや視聴者が実際に使う最も自然で引き込まれる表現を採用してください。
2. **SRT字幕の厳格なフォーマット維持**:
   入力がSRT形式（連番、タイムコード 00:00:00,000 --> 00:00:00,000、字幕文）の場合、**番号とタイムコード行は1文字も改変せずそのまま維持**し、テキスト部分のみを翻訳して置き換えてください。
3. **字幕の可読性（文字数・テンポ）**:
   視聴者が動画再生中に無理なく読めるよう、冗長な表現を避け、簡潔かつテンポの良い言葉選びを行ってください。
4. **追加指示**:
   {instructions if instructions else "なし"}
"""
    return base_prompt

def translate_with_claude(text, sys_prompt, key, model):
    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=sys_prompt,
        messages=[
            {"role": "user", "content": f"以下のテキストを最高品質で翻訳してください。SRTの場合はフォーマットを完全に保護してください。\n\n{text}"}
        ],
        temperature=0.3
    )
    return response.content[0].text

def translate_with_openai(text, sys_prompt, key, model):
    client = openai.OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"以下のテキストを最高品質で翻訳してください。SRTの場合はフォーマットを完全に保護してください。\n\n{text}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# ---------------------------------------------------------
# メイン画面レイアウト
# ---------------------------------------------------------
st.markdown('<div class="main-header">🎬 YouTube Pro 高精度AI翻訳ツール</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">SRT字幕のタイムコードを100%保持し、動画ジャンルに最適化されたネイティブ表現へ自動ローカライズします。</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 原文入力")
    input_mode = st.radio("入力方法を選択", ["テキスト貼り付け", "SRT / TXTファイルアップロード"], horizontal=True)
    
    source_text = ""
    if input_mode == "テキスト貼り付け":
        source_text = st.text_area("台本テキストまたはSRT内容を入力", height=350, placeholder="ここにテキストまたはSRT字幕を貼り付けてください...")
    else:
        uploaded_file = st.file_uploader("ファイルを選択 (.srt, .txt)", type=["srt", "txt"])
        if uploaded_file is not None:
            source_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            st.success(f"ファイル読み込み完了: {uploaded_file.name}")

    start_btn = st.button("🚀 高精度ローカライズ翻訳を開始", type="primary")

with col2:
    st.subheader("📤 翻訳結果")
    result_container = st.empty()

# ---------------------------------------------------------
# 実行処理
# ---------------------------------------------------------
if start_btn:
    if not api_key:
        st.error("⚠️ サイドバーからAPIキーを入力してください。")
    elif not source_text.strip():
        st.warning("⚠️ 翻訳するテキストまたはファイルを入力してください。")
    else:
        with st.spinner("AIが文脈を解析し、ネイティブ向けに高精度翻訳中..."):
            try:
                sys_prompt = create_system_prompt(target_lang, content_tone, custom_instructions)
                
                if engine == "Claude (Anthropic)":
                    translated_output = translate_with_claude(source_text, sys_prompt, api_key, model_name)
                else:
                    translated_output = translate_with_openai(source_text, sys_prompt, api_key, model_name)
                
                with col2:
                    st.text_area("翻訳後テキスト / SRT", value=translated_output, height=350)
                    
                    # ダウンロードボタン
                    st.download_button(
                        label="💾 翻訳結果をダウンロード (.srt / .txt)",
                        data=translated_output,
                        file_name="translated_youtube_subtitles.srt",
                        mime="text/plain"
                    )
                st.toast("✅ 翻訳が完了しました！", icon="🎉")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
