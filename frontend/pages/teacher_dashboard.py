import sys
import base64
from html import escape
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from streamlit_cookies_controller import CookieController

import streamlit as st
from PIL import Image


# ==================================================
# PATHS
# ==================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.connection import SessionLocal
from backend.services.auth_session_service import (
    delete_auth_session,
    get_user_from_token,
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
# RESTORE LOGIN AFTER REFRESH
# ==================================================

if not st.session_state.get("logged_in", False):
    session_token = st.context.cookies.get(
        COOKIE_NAME
    )

    if session_token:
        try:
            with SessionLocal() as session:
                user = get_user_from_token(
                    session=session,
                    token=session_token,
                )

                if user is not None:
                    user_data = {
                        "user_id": user.user_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "role": user.role,
                    }
                else:
                    user_data = None

            if user_data is not None:
                st.session_state.logged_in = True
                st.session_state.user_id = (
                    user_data["user_id"]
                )
                st.session_state.first_name = (
                    user_data["first_name"]
                )
                st.session_state.last_name = (
                    user_data["last_name"]
                )
                st.session_state.email = (
                    user_data["email"]
                )
                st.session_state.role = (
                    user_data["role"]
                )

        except SQLAlchemyError as error:
            print(
                f"Session restoration error: {error}"
            )

# User must be logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")

# User must be a teacher
if st.session_state.get("role") != "teacher":
    st.switch_page("pages/student_dashboard.py")

# ==================================================
# CURRENT TEACHER
# ==================================================

first_name = st.session_state.get("first_name") or "Teacher"
last_name = st.session_state.get("last_name") or ""

teacher_name = escape(
    f"{first_name} {last_name}".strip()
)


# ==================================================
# LOGOUT
# ==================================================

def logout() -> None:
    session_token = st.context.cookies.get(
        COOKIE_NAME
    )

    if session_token:
        try:
            with SessionLocal() as session:
                delete_auth_session(
                    session=session,
                    token=session_token,
                )

        except SQLAlchemyError as error:
            print(
                f"Logout database error: {error}"
            )

    try:
        cookie_controller.remove(
            COOKIE_NAME,
            path="/",
            same_site="strict",
            secure=False,
        )
    except KeyError:
        pass

    authentication_keys = [
        "logged_in",
        "user_id",
        "first_name",
        "last_name",
        "email",
        "role",
    ]

    for key in authentication_keys:
        st.session_state.pop(key, None)

    st.switch_page("app.py")

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
    f'<b>{teacher_name}</b><br>'
    f'<small>Teacher</small>'
    f'</div>'
    f'</div>'

    f'<div class="sidebar-wave"></div>'
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
        logout()


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
