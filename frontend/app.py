import base64
import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

# ==================================================
# ALLOW PYTHON TO FIND THE BACKEND FOLDER
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.connection import SessionLocal
from backend.services.auth_service import authenticate_user

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

CSS_PATH = BASE_DIR / "assets" / "css" / "style.css"
LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"
LOGIN_IMAGE_PATH = BASE_DIR / "assets" / "images" / "login.png"


# ==================================================
# PAGE CONFIG MUST COME FIRST
# ==================================================

logo = Image.open(LOGO_PATH)

st.set_page_config(
    page_title="Quizy | Connexion",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed",
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
# AUTHENTICATION STATE
# ==================================================

AUTH_STATE_DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "first_name": None,
    "last_name": None,
    "email": None,
    "role": None,
    "selected_role": "teacher",
}

for key, default_value in AUTH_STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# ==================================================
# REDIRECT LOGGED-IN USERS
# ==================================================

if st.session_state.logged_in:
    if st.session_state.role == "teacher":
        st.switch_page("pages/teacher_dashboard.py")

    elif st.session_state.role == "student":
        st.switch_page("pages/student_dashboard.py")


# ==================================================
# ROLE SELECTION
# ==================================================

def set_role(role: str) -> None:
    st.session_state.selected_role = role


# ==================================================
# LOGO BASE64
# ==================================================

logo_base64 = base64.b64encode(
    LOGO_PATH.read_bytes()
).decode("utf-8")


# ==================================================
# LOGIN INTERFACE
# ==================================================

with st.container(border=True):
    left, right = st.columns(
        [0.8, 0.8],
        gap="xxsmall",
    )

    with left:
        st.markdown(
            '<div class="left-panel">',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="brand-row">
                <img
                    src="data:image/png;base64,{logo_base64}"
                    class="brand-logo"
                >
                <h1 class="brand-title">Quizy</h1>
            </div>

            <p class="subtitle">
                Votre assistant pédagogique intelligent
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.image(
            str(LOGIN_IMAGE_PATH),
            use_container_width=True,
        )

        st.markdown(
            """<div class="features">
        <div class="feature">
        <div class="feature-icon">Q</div>
        <div><b>Générez</b><br>des QCM et questions</div>
        </div>
        <div class="feature">
        <div class="feature-icon">✓</div>
        <div><b>Évaluez</b><br>vos connaissances</div>
        </div>
        <div class="feature">
        <div class="feature-icon">!</div>
        <div><b>Obtenez</b><br>un feedback instantané</div>
        </div>
        </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="right-panel">',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="form-title">
                <h2>Connexion</h2>
                <p>Connectez-vous pour continuer</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.button(
                "Je suis enseignant",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.selected_role == "teacher"
                    else "secondary"
                ),
                on_click=set_role,
                args=("teacher",),
            )

        with col2:
            st.button(
                "Je suis étudiant",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.selected_role == "student"
                    else "secondary"
                ),
                on_click=set_role,
                args=("student",),
            )

        with st.form("login_form"):
            email = st.text_input(
                "Adresse e-mail",
                placeholder="Entrez votre e-mail",
            )

            password = st.text_input(
                "Mot de passe",
                placeholder="Entrez votre mot de passe",
                type="password",
            )

            submitted = st.form_submit_button(
                "Se connecter",
                use_container_width=True,
            )

        # ==================================================
        # PROCESS LOGIN
        # ==================================================

        if submitted:
            cleaned_email = email.strip().lower()

            if not cleaned_email or not password:
                st.error("Veuillez remplir tous les champs.")

            else:
                try:
                    with SessionLocal() as session:
                        user = authenticate_user(
                            session=session,
                            email=cleaned_email,
                            password=password,
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

                    if user_data is None:
                        st.error(
                            "Adresse e-mail ou mot de passe incorrect."
                        )

                    elif (
                        user_data["role"]
                        != st.session_state.selected_role
                    ):
                        st.error(
                            "Le rôle sélectionné ne correspond pas "
                            "à votre compte."
                        )

                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_data["user_id"]
                        st.session_state.first_name = user_data["first_name"]
                        st.session_state.last_name = user_data["last_name"]
                        st.session_state.email = user_data["email"]
                        st.session_state.role = user_data["role"]

                        if user_data["role"] == "teacher":
                            st.switch_page(
                                "pages/teacher_dashboard.py"
                            )

                        else:
                            st.switch_page(
                                "pages/student_dashboard.py"
                            )

                except SQLAlchemyError as error:
                    print(f"Database login error: {error}")

                    st.error(
                        "Une erreur de base de données "
                        "s'est produite."
                    )

        st.markdown(
            """
            <div class="divider">
                <span></span>ou<span></span>
            </div>

            <button class="google-btn">
                Continuer avec Google
            </button>
            
            <p class="signup">
                Vous n'avez pas de compte ?
                <a href="/register" target="_self">
                 Créer un compte
                </a>
            </p>
    
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )