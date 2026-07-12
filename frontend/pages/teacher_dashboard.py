import streamlit as st
from PIL import Image
import base64
from pathlib import Path

logo=Image.open("frontend/assets/logo.png")

st.set_page_config(
    page_title="Quizy | teacher dashboard",
    page_icon=logo ,
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent.parent
logo_path = BASE_DIR / "assets" / "logo.png"

with open(logo_path, "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #EEF4FF;
    box-shadow: 8px 0 25px rgba(37, 99, 235, 0.08);
}

.sidebar-logo {
    display: flex;
    align-items: center;
    margin-top: -45px;
    margin-bottom: 35px;
}

.sidebar-logo img {
    width: 58px;
    height: 58px;
}

.sidebar-logo h1 {
    font-size: 26px;
    margin: 0;
    color: #5F4BB6;
    font-weight: 800;
}

.sidebar-logo p {
    margin: -4px 0 0 0;
    font-size: 11px;
    color: #64748B;
}

.sidebar-btn {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    margin-bottom: 2px;
    border-radius: 18px;
    color: #1E293B;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
}

.sidebar-btn:hover {
    background: #EEF4FF;
    transform: translateX(6px);
    color: #4F7DF3;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12);
}

.sidebar-btn.active {
     background: #6741F2;
    color: white;
    box-shadow: 0 10px 25px rgba(91, 53, 245, 0.18);
}

.profile-card {
    margin-top: 70px;
    padding: 14px;
    border-radius: 18px;
    background: linear-gradient( 135deg, #EEF4FF, #F4F0FF);
    display: flex;
    align-items: center;
    gap: 12px;
}

.profile-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
     background: linear-gradient(135deg,  #4F7DF3, #8B6DE8);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.sidebar-wave {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 21rem;
    height: 80px;
    background: linear-gradient(135deg, #4F7DF3, #8B6DE8);
    border-radius: 60% 60% 0 0;
    opacity: 0.9;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 25px 25px 25px;
}

.dashboard-header h1 {
    color: #1F1B2E;
    font-size: 30px;
}

.dashboard-header p {
    color: #7C86A5;
    margin-top: 8px;
    font-size: 15px;
}

.header-icons {
    display: flex;
    align-items: center;
    gap: 25px;
    font-size: 22px;
}

.avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: #22B88A;
    color: white;
    display: grid;
    place-items: center;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin: 0 25px;
}

.stat-card {
    background: white;
    border-radius: 18px;
    padding: 24px 22px;
    box-shadow: 0 15px 35px rgba(80, 70, 150, 0.10);
    border: 1px solid #E3E6F5;
    transition: all 0.25s ease;
}

.stat-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 45px rgba(80, 70, 150, 0.16);
}

.stat-icon {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 25px;
    margin-bottom: 18px;
}

.stat-card p {
    color: #2E1A5E;
    font-size: 15px;
    font-weight: 700;
    margin: 0;
}

.stat-card h2 {
    font-size: 34px;
    margin: 10px 0;
    font-weight: 800;
}

.stat-card small {
    font-weight: 700;
}

.stat-card.green .stat-icon {
    background: #E8F8F3;
    color: #22B88A;
}

.stat-card.green h2,
.stat-card.green small {
    color: #22B88A;
}

.stat-card.orange .stat-icon {
    background: #FFF4E5;
    color: #F97316;
}

.stat-card.orange h2,
.stat-card.orange small {
    color: #F97316;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
          <img
            src="data:image/png;base64,{logo_base64}"
            alt="Logo"
            class="logo"
        >
        <div>
            <h1>Quizy</h1>
            <p>Teach. Assess. Grow.</p>
        </div>
    </div>

    <div class="sidebar-btn active">▦ Dashboard</div>
    <div class="sidebar-btn">📄 Documents</div>
    <div class="sidebar-btn">🧾 Quizzes</div>
    <div class="sidebar-btn">👥 Students</div>
    <div class="sidebar-btn">◷ Analytics</div>
    <div class="sidebar-btn">⚙ Settings</div>

    <div class="profile-card">
        <div class="profile-avatar">👤</div>
        <div>
            <b>Mme. Amira</b><br>
            <small>Teacher</small>
        </div>
    </div>

    <div class="sidebar-btn">↪ Logout</div>
    <div class="sidebar-wave"></div>
    """, unsafe_allow_html=True)

st.markdown(
"""
<div class="dashboard-header">
<div>
<h1>Welcome back, Mme. Amira! 👋</h1>
<p>Here’s what’s happening in your classroom.</p>
</div>

<div class="header-icons">
<span>🔔</span>
<div class="avatar">👤</div>
</div>
</div>

<div class="stats-grid">

<div class="stat-card green">
<div class="stat-icon">📄</div>
<p>Uploaded Documents</p>
<h2>12</h2>
<small>+2 this week</small>
</div>

<div class="stat-card orange">
<div class="stat-icon">🧾</div>
<p>Generated Quizzes</p>
<h2>28</h2>
<small>+5 this week</small>
</div>

<div class="stat-card green">
<div class="stat-icon">👥</div>
<p>Active Students</p>
<h2>156</h2>
<small>+18 this week</small>
</div>

<div class="stat-card orange">
<div class="stat-icon">🕘</div>
<p>Recent Quizzes</p>
<h2>7</h2>
<small>+3 this week</small>
</div>

</div>
""",
unsafe_allow_html=True
)