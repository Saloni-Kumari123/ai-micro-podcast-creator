import streamlit as st

# ---------------- 1. PAGE CONFIG ----------------
st.set_page_config(page_title="Dashboard | AI Podcast", layout="wide", initial_sidebar_state="expanded")

# ---------------- 2. MODERN CSS ----------------
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f8f9fa; }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #2575fc; }
    
    /* Navigation Card Styling */
    .nav-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        transition: 0.3s;
    }
    .nav-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ---------------- 3. AUTH CHECK ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access your dashboard.")
    st.stop()

# ---------------- 4. SIDEBAR ----------------
with st.sidebar:
    st.title("🎧 AI Podcast")
    st.markdown(f"**Logged in as:** \n{st.session_state.get('username', 'User')}")
    st.write("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- 5. MAIN CONTENT ----------------
st.title(f"Welcome back, {st.session_state.get('username', 'User')} 👋")
st.write("Here is what's happening with your podcasts today.")

# --- Row 1: Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Podcasts", "12", "+2")
col2.metric("Minutes Generated", "45m", "+5m")
col3.metric("Storage Used", "128MB", "12%")
col4.metric("Credits Left", "85", "-5")

st.write("---")

# --- Row 2: Quick Actions ---
st.subheader("🚀 Quick Actions")
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    st.markdown("""
    <div class="nav-card">
        <h3>🎙️ Create New</h3>
        <p>Start a new AI voiceover or podcast episode from a topic.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Creator", key="nav_create", use_container_width=True):
        st.switch_page("pages/4_podcast.py") # Make sure the filename matches your structure

with action_col2:
    st.markdown("""
    <div class="nav-card">
        <h3>📁 My Library</h3>
        <p>Listen to, download, or manage your previously generated audio.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Library", key="nav_lib", use_container_width=True):
        st.info("Library feature coming soon!")

with action_col3:
    st.markdown("""
    <div class="nav-card">
        <h3>⚙️ Settings</h3>
        <p>Update your profile, change voices, or manage subscription.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Edit Profile", key="nav_settings", use_container_width=True):
        st.info("Settings coming soon!")

# --- Row 3: Recent Activity ---
st.write("---")
st.subheader("🕒 Recent Activity")
activity_data = {
    "Date": ["2026-03-30", "2026-03-28", "2026-03-25"],
    "Podcast Name": ["Tech Trends 2026", "AI in Healthcare", "Morning News Summary"],
    "Status": ["Completed", "Completed", "Completed"]
}
st.table(activity_data)