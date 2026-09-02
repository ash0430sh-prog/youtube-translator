import streamlit as st
import streamlit as st

# ==========================================
# STRIPE 決済リンク設定
# ==========================================
STRIPE_PAYMENT_URL = "https://buy.stripe.com/aFacN72GA4KiaIb9T46sw00"

# --- サイドバー側の案内エリア ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### ⚡ PRO LICENSE")
    
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
                ">
                    🚀 PROプランに登録（初月無料）
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.caption("※ クーポンコード入力で初回30日間¥0でお試しいただけます")
