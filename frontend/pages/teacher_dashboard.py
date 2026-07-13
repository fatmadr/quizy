import base64
from pathlib import Path

import streamlit as st
from PIL import Image


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CSS_PATH = BASE_DIR / "assets" / "css" / "style.css"
LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"
ICONS_DIR = BASE_DIR / "assets" / "icons"


# ==================================================
# PAGE CONFIG MUST BE FIRST
# ==================================================

logo = Image.open(LOGO_PATH)

st.set_page_config(
    page_title="Quizy | Teacher Dashboard",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# LOAD CSS
# ==================================================

css = CSS_PATH.read_text(encoding="utf-8")

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True,
)


# ==================================================
# LOAD LOGO
# ==================================================

logo_base64 = base64.b64encode(
    LOGO_PATH.read_bytes()
).decode("utf-8")


# ==================================================
# SVG FUNCTIONS
# ==================================================

def load_svg(icon_name: str) -> str:
    icon_path = ICONS_DIR / icon_name

    if not icon_path.exists():
        return ""

    return icon_path.read_text(encoding="utf-8")


def sidebar_item(
    label: str,
    icon_name: str,
    active: bool = False,
) -> str:
    icon = load_svg(icon_name)
    active_class = " active" if active else ""

    # No indentation before the HTML tags
    return (
        f'<div class="sidebar-btn{active_class}">'
        f'<span class="sidebar-icon">{icon}</span>'
        f'<span>{label}</span>'
        f'</div>'
    )


# ==================================================
# SIDEBAR
# ==================================================

sidebar_html = (
    f'<div class="sidebar-logo">'
    f'<img src="data:image/png;base64,{logo_base64}" '
    f'alt="Quizy logo" class="logo">'
    f'<div class="sidebar-brand-text">'
    f'<h1>Quizy</h1>'
    f'<p>Teach. Assess. Grow.</p>'
    f'</div>'
    f'</div>'

    f'{sidebar_item("Dashboard", "dashboard.svg", active=True)}'
    f'{sidebar_item("Documents", "document.svg")}'
    f'{sidebar_item("Quizzes", "quiz.svg")}'
    f'{sidebar_item("Students", "student.svg")}'
    f'{sidebar_item("Analytics", "analytics.svg")}'
    f'{sidebar_item("Settings", "settings.svg")}'

    f'<div class="profile-card">'
    f'<div class="profile-avatar">👤</div>'
    f'<div>'
    f'<b>Mme. Amira</b><br>'
    f'<small>Teacher</small>'
    f'</div>'
    f'</div>'

    f'<div class="sidebar-btn">'
    f'<span class="sidebar-logout-icon">↪</span>'
    f'<span>Logout</span>'
    f'</div>'

    f'<div class="sidebar-wave"></div>'
)

with st.sidebar:
    st.markdown(
        sidebar_html,
        unsafe_allow_html=True,
    )


# ==================================================
# DASHBOARD CONTENT
# ==================================================

dashboard_html = (
    '<div class="dashboard-header">'
        '<div>'
            '<h1>Welcome back, Mme. Amira! 👋</h1>'
            '<p>Here’s what’s happening in your classroom.</p>'
        '</div>'
        '<div class="header-icons">'
            '<span>🔔</span>'
            '<div class="avatar">👤</div>'
        '</div>'
    '</div>'

    '<div class="stats-grid">'
        '<div class="stat-card green">'
            '<div class="stat-icon">📄</div>'
            '<p>Uploaded Documents</p>'
            '<h2>12</h2>'
            '<small>+2 this week</small>'
        '</div>'

        '<div class="stat-card orange">'
            '<div class="stat-icon">🧾</div>'
            '<p>Generated Quizzes</p>'
            '<h2>28</h2>'
            '<small>+5 this week</small>'
        '</div>'

        '<div class="stat-card green">'
            '<div class="stat-icon">👥</div>'
            '<p>Active Students</p>'
            '<h2>156</h2>'
            '<small>+18 this week</small>'
        '</div>'

        '<div class="stat-card orange">'
            '<div class="stat-icon">🕘</div>'
            '<p>Recent Quizzes</p>'
            '<h2>7</h2>'
            '<small>+3 this week</small>'
        '</div>'
    '</div>'
)

st.markdown(
    dashboard_html,
    unsafe_allow_html=True,
)
