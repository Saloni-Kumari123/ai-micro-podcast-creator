import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:5000/auth"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Login", layout="centered", initial_sidebar_state="collapsed")

# ---------------- STYLE ----------------
st.markdown("""
<style>
    /* Hide sidebar on login page */
    [data-testid="stSidebar"] {display: none;}
    
    .stApp { background-color: #f8f9fa; }
    
    /* Primary Gradient Button */
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white; border: none; border-radius: 10px;
        height: 3em; width: 100%; transition: 0.3s;
    }
    
    /* Secondary link-style buttons */
    .secondary-btn > div > button {
        background: transparent !important;
        color: #2575fc !important;
        border: 1px solid #2575fc !important;
        height: 2.5em !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION & REDIRECT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page("pages/5_Dashboard.py")

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center;'>🔐 AI Podcast Login</h1>", unsafe_allow_html=True)

with st.container(border=True):
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="yourname@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    # Extra Navigation Links (Styled differently)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("📝 Register Account", key="goto_reg"):
            st.switch_page("pages/1_Register.py")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🔑 Forgot Pass?", key="goto_forgot"):
            st.switch_page("pages/3_Forgot_Password.py")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGIC ----------------
if submit:
    if not email or not password:
        st.warning("⚠️ Please enter credentials.")
    else:
        with st.spinner("Authenticating..."):
            try:
                # Set a timeout so the app doesn't hang forever if Flask is down
                res = requests.post(f"{API_URL}/login", json={"email": email, "password": password}, timeout=5)
                data = res.json()

                if res.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user_email = data["user"]["email"]
                    st.session_state.username = data["user"]["username"]
                    st.success("🎉 Welcome back!")
                    st.switch_page("pages/5_Dashboard.py")
                else:
                    st.error(data.get("error", "❌ Check your email/password."))
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend server is offline.")
            except Exception as e:
                st.error("❌ An unexpected error occurred.")