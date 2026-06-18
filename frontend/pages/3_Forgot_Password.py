import streamlit as st
import requests
import re

API_URL = "http://127.0.0.1:5000/otp"

st.set_page_config(page_title="Recover Account", layout="centered")

# --- UI STATE ---
if "fp_step" not in st.session_state: st.session_state.fp_step = "Send OTP"
if "fp_email" not in st.session_state: st.session_state.fp_email = ""

def safe_request(endpoint, payload):
    try:
        res = requests.post(f"{API_URL}/{endpoint}", json=payload, timeout=10)
        return res.status_code, res.json()
    except:
        return 500, {"error": "Server unreachable"}

st.title("🔑 Password Recovery")

with st.container(border=True):
    # STEP 1: SEND
    if st.session_state.fp_step == "Send OTP":
        email = st.text_input("Registered Email Address")
        if st.button("Send Reset Code", use_container_width=True):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email.")
            else:
                with st.spinner("Verifying email..."):
                    status, data = safe_request("forgot-password", {"email": email})
                    if status == 200:
                        st.session_state.fp_email = email
                        st.session_state.fp_step = "Verify OTP"
                        st.rerun()
                    else:
                        st.error(data.get("error", "Error sending OTP"))

    # STEP 2: VERIFY
    elif st.session_state.fp_step == "Verify OTP":
        st.info(f"Code sent to: {st.session_state.fp_email}")
        otp_code = st.text_input("Enter 6-Digit Code", maxlength=6)
        if st.button("Verify & Continue", use_container_width=True):
            status, data = safe_request("verify-otp", {"email": st.session_state.fp_email, "otp": otp_code})
            if status == 200:
                st.session_state.fp_step = "Reset Password"
                st.rerun()
            else:
                st.error("Invalid Code. Please try again.")
        if st.button("← Back"):
            st.session_state.fp_step = "Send OTP"
            st.rerun()

    # STEP 3: RESET
    elif st.session_state.fp_step == "Reset Password":
        new_pw = st.text_input("New Password", type="password")
        conf_pw = st.text_input("Confirm Password", type="password")
        if st.button("Reset Password", use_container_width=True):
            if new_pw != conf_pw:
                st.error("Passwords do not match!")
            elif len(new_pw) < 8:
                st.error("Password must be 8+ characters.")
            else:
                status, data = safe_request("reset-password", {"email": st.session_state.fp_email, "new_password": new_pw})
                if status == 200:
                    st.success("Password updated! Redirecting...")
                    st.session_state.fp_step = "Send OTP"
                    st.switch_page("login.py")
                else:
                    st.error("Update failed. Try again.")