import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# Allow Python to find the backend folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.database.connection import SessionLocal
from backend.services.auth_service import register_user
from backend.services.user_service import get_user_by_email


# ==================================================
# PATHS
# ==================================================

FRONTEND_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = FRONTEND_DIR / "assets" / "images" / "logo.png"
CSS_PATH = FRONTEND_DIR / "assets" / "css" / "style.css"

logo = Image.open(LOGO_PATH)


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Quizy | Créer un compte",
    page_icon=logo,
    layout="centered",
    initial_sidebar_state="collapsed",
)

#========CSS====================

css = CSS_PATH.read_text(encoding="utf-8")
st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="register-page-marker"></div>',
    unsafe_allow_html=True,
)

# ==================================================
# PAGE TITLE
# ==================================================

st.title("Créer un compte")


# ==================================================
# DEFAULT ROLE
# ==================================================

selected_role = st.session_state.get(
    "selected_role",
    "student",
)

role_index = 0 if selected_role == "teacher" else 1


# ==================================================
# REGISTRATION FORM
# ==================================================

with st.form("registration_form"):
    first_name = st.text_input(
        "Prénom",
        placeholder="Entrez votre prénom",
    )

    last_name = st.text_input(
        "Nom",
        placeholder="Entrez votre nom",
    )

    email = st.text_input(
        "Adresse e-mail",
        placeholder="Entrez votre adresse e-mail",
    )

    role = st.selectbox(
        "Rôle",
        options=["teacher", "student"],
        index=role_index,
        format_func=lambda value: (
            "Enseignant"
            if value == "teacher"
            else "Étudiant"
        ),
    )

    password = st.text_input(
        "Mot de passe",
        type="password",
        placeholder="Minimum 8 caractères",
    )

    confirm_password = st.text_input(
        "Confirmer le mot de passe",
        type="password",
        placeholder="Confirmez votre mot de passe",
    )

    submitted = st.form_submit_button(
        "Créer mon compte",
        use_container_width=True,
    )


# ==================================================
# PROCESS REGISTRATION
# ==================================================

if submitted:
    cleaned_first_name = first_name.strip()
    cleaned_last_name = last_name.strip()
    cleaned_email = email.strip().lower()

    if (
        not cleaned_first_name
        or not cleaned_last_name
        or not cleaned_email
        or not password
        or not confirm_password
    ):
        st.error("Veuillez remplir tous les champs.")

    elif password != confirm_password:
        st.error("Les mots de passe ne correspondent pas.")

    else:
        try:
            with SessionLocal() as session:
                existing_user = get_user_by_email(
                    session=session,
                    email=cleaned_email,
                )

                if existing_user is not None:
                    st.error(
                        "Un compte existe déjà avec "
                        "cette adresse e-mail."
                    )

                else:
                    register_user(
                        session=session,
                        first_name=cleaned_first_name,
                        last_name=cleaned_last_name,
                        email=cleaned_email,
                        password=password,
                        role=role,
                    )

                    st.session_state.account_created = True

                    st.switch_page("app.py")

        except ValueError as error:
            st.error(str(error))

        except IntegrityError:
            st.error(
                "Un compte existe déjà avec "
                "cette adresse e-mail."
            )

        except SQLAlchemyError as error:
            print(f"Registration database error: {error}")

            st.error(
                "Une erreur de base de données "
                "s'est produite."
            )


# ==================================================
# RETURN TO LOGIN
# ==================================================

if st.button(
    "Retour à la connexion",
    use_container_width=True,
):
    st.switch_page("app.py")