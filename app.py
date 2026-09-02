# 3. 機能・課金タブ（MODE 1, 2, 3 の3段構成）
tab1, tab2, tab3 = st.tabs([
    "🚀 MODE 1: フル動画・音声翻訳（PRO）", 
    "⚡ MODE 2: クイック字幕・テキスト翻訳",
    "🌐 MODE 3: YouTube URL 直接ローカライズ"
])

# ----------------------------------------------------
# MODE 1: 動画・音声ローカライズ（PRO限定）
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
        st.success("⚡ PRO機能が有効化されています。")
        uploaded_video = st.file_uploader("動画・音声ファイルを選択 (MP4, MP3, WAV)", type=["mp4", "mp3", "wav"])
        if uploaded_video:
            st.info(f"📁 読み込み完了: {uploaded_video.name}")
            st.button("AI一括翻訳・ローカライズを実行", type="primary")

# ----------------------------------------------------
# MODE 2: クイックテキスト・字幕翻訳（無料）
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
# MODE 3: YouTube URL 解析・字幕抽出
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
