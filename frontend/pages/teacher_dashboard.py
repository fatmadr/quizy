import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from streamlit_cookies_controller import CookieController


# ==================================================
# PATHS
# ==================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.connection import SessionLocal

from backend.services.dashboard_service import (
    get_teacher_dashboard_stats,
)

from frontend.components.sidebar import (
    build_teacher_sidebar,
)

from frontend.utils.auth_helpers import (
    get_current_user_name,
    logout_user,
    require_role,
)


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
# COOKIE
# ==================================================

COOKIE_NAME = "quizy_session"

cookie_controller = CookieController(
    key="teacher_dashboard_cookie",
)

# ==================================================
# PROTECT TEACHER PAGE
# ==================================================

require_role(
    required_role="teacher",
    wrong_role_page="pages/student_dashboard.py",
)

# ==================================================
# CURRENT TEACHER
# ==================================================

teacher_name = get_current_user_name(
    default_name="Teacher",
)


# ==================================================
# DASHBOARD STATISTICS
# ==================================================

try:
    with SessionLocal() as session:
        dashboard_stats = get_teacher_dashboard_stats(
            session=session,
            teacher_id=st.session_state["user_id"],
        )

except SQLAlchemyError as error:
    print(
        f"Dashboard statistics error: {error}"
    )

    dashboard_stats = {
        "documents": 0,
        "quizzes": 0,
        "students": 0,
        "recent_quizzes": 0,
    }

    st.error(
        "Dashboard statistics could not be loaded."
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
# SIDEBAR
# ==================================================

sidebar_html = build_teacher_sidebar(
    logo_path=LOGO_PATH,
    icons_dir=ICONS_DIR,
    teacher_name=teacher_name,
    active_page="dashboard",
)

with st.sidebar:
    st.markdown(
        sidebar_html,
        unsafe_allow_html=True,
    )

    if st.button(
            "↪ Logout",
            key="logout_button",
            use_container_width=True,
    ):
        logout_user(cookie_controller)


# ==================================================
# DASHBOARD CONTENT
# ==================================================

dashboard_html = (
    '<div class="dashboard-header">'
        '<div>'
            f'<h1>Welcome back, {teacher_name}! 👋</h1>'
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
            f'<h2>{dashboard_stats["documents"]}</h2>'
        '</div>'
    
        '<div class="stat-card orange">'
            '<div class="stat-icon">🧾</div>'
            '<p>Generated Quizzes</p>'
            f'<h2>{dashboard_stats["quizzes"]}</h2>'
        '</div>'
    
        '<div class="stat-card green">'
            '<div class="stat-icon">👥</div>'
            '<p>Active Students</p>'
            f'<h2>{dashboard_stats["students"]}</h2>'
        '</div>'
    
        '<div class="stat-card orange">'
            '<div class="stat-icon">🕘</div>'
            '<p>Recent Quizzes</p>'
            f'<h2>{dashboard_stats["recent_quizzes"]}</h2>'
        '</div>'
    
    '</div>'
)

st.markdown(
    dashboard_html,
    unsafe_allow_html=True,
)
