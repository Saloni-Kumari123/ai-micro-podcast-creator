import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:5000/auth"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Register", layout="centered")

# ---------------- MODERN STYLE ----------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Center the Title */
    h1 {
        padding-bottom: 1rem;
        color: #1E1E1E;
    }

    /* Gradient Button */
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 117, 252, 0.3);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- VALIDATION FUNCTIONS ----------------
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def is_strong_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password)

# ---------------- UI LAYOUT ----------------
st.markdown("<h1 style='text-align:center;'>🎙️ Join AI Podcast Creator</h1>", unsafe_allow_html=True)

# Using st.container with border for the "Card" effect
with st.container(border=True):
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="johndoe")
        email = st.text_input("Email", placeholder="name@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password", type="password", help="8+ chars, 1 uppercase, 1 number")
        with col2:
            confirm_pass = st.text_input("Confirm Password", type="password")
            
        submit = st.form_submit_button("Create Account", use_container_width=True)

    # Secondary Action
    st.markdown("<p style='text-align:center; font-size: 0.9rem;'>Already have an account? <a href='#'>Login here</a></p>", unsafe_allow_html=True)

# ---------------- LOGIC ----------------
if submit:
    if not (username and email and password):
        st.warning("⚠️ Please fill in all fields.")
    elif not is_valid_email(email):
        st.error("❌ That email doesn't look right.")
    elif not is_strong_password(password):
        st.error("❌ Password is too weak.")
    elif password != confirm_pass:
        st.error("❌ Passwords do not match.")
    else:
        with st.spinner("Creating your account..."):
            try:
                res = requests.post(
                    f"{API_URL}/register",
                    json={"username": username, "email": email, "password": password},
                    timeout=5 # Always set a timeout for API calls
                )
                if res.status_code == 201:
                    st.success("🎉 Welcome aboard! Redirecting...")
                    st.balloons()
                    # Logic to switch to login view
                    st.session_state.page = "login" 
                    st.rerun()
                else:
                    st.error(res.json().get("error", "Registration failed"))
            except Exception:
                st.error("❌ Server is offline. Please try again later.")