import streamlit as st
import requests
import time

# --- CONFIG ---
st.set_page_config(page_title="AI Podcast Creator", page_icon="🎧", layout="wide")
API_BASE = "http://127.0.0.1:5000"

# --- CUSTOM CSS (No Sidebar, Modern Cards) ---
st.markdown("""
<style>
    [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {display: none;}
    .stApp { background-color: #f8f9fa; }
    .hero { text-align: center; padding: 3rem 0; }
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white; border-radius: 10px; height: 3em; width: 100%; border: none;
    }
    .secondary-btn > div > button {
        background: transparent !important; color: #2575fc !important;
        border: 1px solid #2575fc !important;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "fp_step" not in st.session_state: st.session_state.fp_step = "email"

def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 1. LANDING PAGE ---
if st.session_state.page == "landing":
    st.markdown('<div class="hero"><h1>🎙️ Welcome to AI Podcast Creator</h1><p>Generate professional scripts and audio using AI.</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("✨ Use AI to turn any topic into a 2-person podcast conversation instantly.")
        if st.button("Get Started (Register)"): switch_page("register")
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("Already have an account? Login"): switch_page("login")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. REGISTER PAGE ---
elif st.session_state.page == "register":
    st.markdown("<h2 style='text-align:center;'>📝 Create Account</h2>", unsafe_allow_html=True)
    with st.container():
        reg_email = st.text_input("Email")
        reg_user = st.text_input("Username")
        reg_pass = st.text_input("Password", type="password")
        if st.button("Register"):
            try:
                res = requests.post(f"{API_BASE}/auth/register", json={"email": reg_email, "username": reg_user, "password": reg_pass}, timeout=10)
                if res.status_code == 201:
                    st.success("🎉 Registered! Please Login.")
                    time.sleep(1)
                    switch_page("login")
                else:
                    st.error(res.json().get("error", "Registration Failed"))
            except requests.exceptions.RequestException:
                st.error("❌ Could not connect to backend. Try again.")
        if st.button("Back to Login", key="reg_back"): switch_page("login")

# --- 3. LOGIN PAGE ---
elif st.session_state.page == "login":
    st.markdown("<h2 style='text-align:center;'>🔐 Login</h2>", unsafe_allow_html=True)
    with st.container():
        login_email = st.text_input("Email")
        login_pass = st.text_input("Password", type="password")
        if st.button("Sign In"):
            try:
                res = requests.post(f"{API_BASE}/auth/login", json={"email": login_email, "password": login_pass}, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.logged_in = True
                    st.session_state.username = data["user"]["username"]
                    st.session_state.user_email = data["user"]["email"]
                    switch_page("app")
                else:
                    st.error("❌ Invalid Email or Password")
            except requests.exceptions.RequestException:
                st.error("❌ Could not connect to backend. Try again.")
        col_l, col_r = st.columns(2)
        with col_l:
            if st.button("Forgot Password?", key="go_fp"): switch_page("forgot_password")
        with col_r:
            if st.button("New User?", key="go_reg"): switch_page("register")

# --- 4. FORGOT PASSWORD (OTP FLOW) ---
elif st.session_state.page == "forgot_password":
    st.markdown("<h2 style='text-align:center;'>🔑 Reset Password</h2>", unsafe_allow_html=True)
    with st.container():
        if st.session_state.fp_step == "email":
            fp_email = st.text_input("Enter Registered Email")
            if st.button("Send OTP"):
                try:
                    res = requests.post(f"{API_BASE}/otp/forgot-password", json={"email": fp_email}, timeout=10)
                    if res.status_code == 200:
                        st.session_state.reset_email = fp_email
                        st.session_state.fp_step = "otp"
                        st.rerun()
                    else:
                        st.error(res.text)
                except requests.exceptions.RequestException:
                    st.error("❌ Could not connect to backend.")
        elif st.session_state.fp_step == "otp":
            otp = st.text_input("Enter 6-Digit OTP")
            new_p = st.text_input("New Password", type="password")
            if st.button("Reset Password"):
                try:
                    res = requests.post(f"{API_BASE}/otp/reset-password", json={"email": st.session_state.reset_email, "otp": otp, "new_password": new_p}, timeout=10)
                    if res.status_code == 200:
                        st.success("✅ Password Changed!")
                        st.session_state.fp_step = "email"
                        switch_page("login")
                    else:
                        st.error(res.text)
                except requests.exceptions.RequestException:
                    st.error("❌ Could not connect to backend.")
        if st.button("Cancel"): switch_page("login")

# --- 5. MAIN GENERATOR APP ---
elif st.session_state.page == "app":
    if not st.session_state.logged_in: switch_page("login")
    
    st.title(f"🎧 Hello, {st.session_state.username}!")
    col_in, col_out = st.columns([1, 1.2])
    
    with col_in:
        st.subheader("Podcast Settings")
        topic = st.text_area("What is the topic?", placeholder="Quantum Physics for kids...")
        voice = st.selectbox("Voice", ["Professional Male", "Friendly Female"])
        
        if st.button("🎙️ Generate Podcast"):
            if not topic.strip():
                st.warning("⚠️ Please enter a topic.")
            else:
                with st.spinner("AI is generating your podcast... 🎧"):
                    try:
                        res = requests.post(f"{API_BASE}/podcast/generate-podcast",
                                            json={"topic": topic, "voice": voice},
                                            timeout=20)
                        if res.status_code == 200:
                            st.session_state.audio_bytes = res.content
                            st.success("✅ Podcast generated successfully!")
                        else:
                            st.error(f"❌ Error: {res.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Could not connect to backend. Make sure the server is running.")
                    except requests.exceptions.Timeout:
                        st.error("❌ Request timed out. Try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Unexpected error: {e}")
    
    with col_out:
        st.subheader("Your Result")
        if "audio_bytes" in st.session_state:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")
            st.download_button("⬇️ Download MP3", st.session_state.audio_bytes, "podcast.mp3", "audio/mp3")
        else:
            st.info("Enter a topic and click Generate to see your podcast here.")