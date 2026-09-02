# ==========================================
# STRIPE 決済リンク設定
# ==========================================
STRIPE_PAYMENT_URL = "https://buy.stripe.com/aFacN72GA4KiaIb9T46sw00"

# --- サイドバー側の案内エリア ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### ⚡ PRO LICENSE")
    
    # ライセンス未認証ユーザーへの案内
    if not st.session_state.get("is_pro", False):
        st.markdown(
            f"""
            <a href="{STRIPE_PAYMENT_URL}" target="_blank" style="text-decoration: none;">
                <div style="
                    background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
                    color: #050811;
                    font-weight: 800;
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
                    margin-bottom: 12px;
                    transition: transform 0.2s;
                ">
                    🚀 PROプランに登録（初月無料）
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.caption("※ クーポンコード入力で初回30日間¥0でお試しいただけます")

# --- PRO限定機能（MODE 1等）のロック画面 ---
def show_pro_lock_banner():
    st.markdown(
        f"""
        <div style="
            background: rgba(11, 20, 38, 0.85);
            border: 2px solid #FF007F;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.3);
            margin: 20px 0;
        ">
            <h3 style="color: #FF007F; margin-bottom: 8px;">🔒 PRO FEATURE LOCKED</h3>
            <p style="color: #E2E8F0; font-size: 14px; margin-bottom: 18px;">
                この機能を利用するには TRANSLY PRO の有効化が必要です。<br>
                高精度な音声解析・一括字幕生成・多言語翻訳エンジンが無制限で利用可能になります。
            </p>
            <a href="{STRIPE_PAYMENT_URL}" target="_blank" style="text-decoration: none;">
                <span style="
                    background: #FF007F;
                    color: #FFFFFF;
                    font-weight: bold;
                    padding: 10px 24px;
                    border-radius: 6px;
                    box-shadow: 0 0 15px rgba(255, 0, 127, 0.5);
                    display: inline-block;
                ">
                    ⚡ 今すぐ初月無料でPROを体験する
                </span>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
