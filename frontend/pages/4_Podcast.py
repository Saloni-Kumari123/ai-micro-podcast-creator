import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:5000/podcast"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Podcast Generator", layout="wide", page_icon="🎙️")

# ---------------- MODERN STYLE ----------------
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white; border-radius: 10px; border: none; height: 3.5em; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Workspace")
    st.markdown(f"👤 **User:** {st.session_state.get('username', 'Creator')}")
    st.write("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("login.py")

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.stop()

# ---------------- MAIN UI ----------------
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("# 🎙️ Create Podcast")
    with st.container(border=True):
        topic = st.text_area("✍️ Topic or Script Segment", 
                             placeholder="e.g., The impact of quantum computing...",
                             help="Enter a detailed topic.")
        
        c1, c2 = st.columns(2)
        with c1:
            voice = st.selectbox("🗣️ Voice Persona", ["Professional Male", "Friendly Female", "News Anchor"])
        with c2:
            length = st.select_slider("⏳ Duration", options=["Short", "Medium", "Long"])
            
        generate = st.button("🚀 Generate Now", use_container_width=True)

with col2:
    st.markdown("### 🎧 Your Generated Audio")
    
    if generate:
        if not topic:
            st.warning("⚠️ Please provide a topic first.")
        else:
            with st.status("🪄 AI at work...", expanded=True) as status:
                st.write("📝 Preparing request...")
                
                # DATA PAYLOAD
                # Note: We include 'topic' specifically in case the backend 
                # is strictly looking for that key to avoid 400 errors.
                payload = {
                    "topic": topic, 
                    "voice": voice, 
                    "length": length
                }

                try:
                    res = requests.post(
                        f"{API_URL}/generate-podcast", 
                        json=payload,
                        timeout=120 # Increased timeout for heavy AI processing
                    )
                    
                    if res.status_code == 200:
                        status.update(label="✅ Podcast Ready!", state="complete", expanded=False)
                        with st.container(border=True):
                            st.audio(res.content, format="audio/mp3")
                            st.download_button(
                                label="⬇️ Download MP3",
                                data=res.content,
                                file_name=f"podcast_{int(time.time())}.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                    else:
                        # DEBUG: This helps you see WHY the backend returned 400
                        status.update(label=f"❌ Error {res.status_code}", state="error")
                        st.error(f"Backend Message: {res.text}")
                        st.info("Check if your Flask route expects 'topic' as a JSON key.")
                        
                except Exception as e:
                    status.update(label="❌ Connection Error", state="error")
                    st.error(f"Could not reach backend: {e}")
    else:
        st.info("Your audio will appear here.")