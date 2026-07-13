import streamlit as st
from PIL import Image
from pathlib import Path
import base64

css_path = Path(__file__).resolve().parent.parent / "assets" / "css" / "style.css"
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

logo=Image.open("frontend/assets/images/logo.png")

st.set_page_config(
    page_title="Quizy | Connexion",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "role" not in st.session_state:
    st.session_state.role = "teacher"


def set_role(role: str):
    st.session_state.role = role

with st.container(border=True):
    left, right = st.columns([0.8, 0.8], gap="xxsmall")

with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"
    logo_base64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

    st.markdown(f"""
    <div class="brand-row">
    <img src="data:image/png;base64,{logo_base64}" class="brand-logo">
    <h1 class="brand-title">Quizy</h1>
    </div>
        <p class="subtitle">Votre assistant pédagogique intelligent</p>
    """, unsafe_allow_html=True)

    IMAGE_PATH = BASE_DIR / "assets" /"images" / "login.png"
    st.image(str(IMAGE_PATH), use_container_width=True)

    st.markdown("""
        <div class="features">
            <div class="feature"><div class="feature-icon">Q</div><div><b>Générez</b><br>des QCM et questions</div></div>
            <div class="feature"><div class="feature-icon">✓</div><div><b>Évaluez</b><br>vos connaissances</div></div>
            <div class="feature"><div class="feature-icon">!</div><div><b>Obtenez</b><br>un feedback instantané</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown("""
    <div class="form-title">
        <h2>Connexion</h2>
        <p>Connectez-vous pour continuer</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Je suis enseignant",
            use_container_width=True,
            type="primary" if st.session_state.role == "teacher" else "secondary",
            on_click=set_role,
            args=("teacher",),
        )

    with col2:
        st.button(
            "Je suis étudiant",
            use_container_width=True,
            type="primary" if st.session_state.role == "student" else "secondary",
            on_click=set_role,
            args=("student",),
        )

    with st.form("login_form"):
        email = st.text_input("Adresse e-mail", placeholder="Entrez votre e-mail")
        password = st.text_input(
            "Mot de passe",
            placeholder="Entrez votre mot de passe",
            type="password",
        )

        submitted = st.form_submit_button("Se connecter", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Veuillez remplir tous les champs.")
        else:
            role = "enseignant" if st.session_state.role == "teacher" else "étudiant"
            st.success(f"Connexion {role} réussie.")

    st.markdown("""
        <div class="divider"><span></span>ou<span></span></div>
        <button class="google-btn">Continuer avec Google</button>
        <p class="signup">
            Vous n'avez pas de compte ?
            <a href="#">Créer un compte</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
