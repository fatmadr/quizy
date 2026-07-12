import streamlit as st
from PIL import Image
from pathlib import Path
import base64

logo=Image.open("frontend/assets/logo.png")

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

st.markdown("""
<style>
:root {
    --purple-darkest: #2E1A5E;
    --purple-primary: #5B35F5;
    --purple-medium: #6741F2;
    --purple-dark: #431DE0;
    --purple-soft: #EDE9FE;
    --purple-pale: #F5F3FF;

    --bg-main: #FBFCFF;
    --bg-secondary: #F6F7FF;
    --bg-card: #FFFFFF;
    --bg-soft: #F8F7FF;

    --text-primary: #2E1A5E;
    --text-secondary: #526089;
    --text-muted: #7C86A5;
    --text-light: #9CA3B8;

    --border-primary: #D9DFF1;
    --border-soft: #E3E6F5;
    --border-purple: #CFC5FF;

    --success: #22B88A;
    --success-soft: #E8F8F3;
    --warning: #F4A340;
    --warning-soft: #FFF4E5;
    --danger: #E85D75;
    --danger-soft: #FDECEF;
    --info: #5B8DEF;
    --info-soft: #EDF4FF;

    --shadow-soft: 0 10px 25px rgba(80, 70, 150, 0.08);
    --shadow-card: 0 15px 35px rgba(80, 70, 150, 0.12);
    --shadow-purple: 0 10px 25px rgba(91, 53, 245, 0.18);
[data-testid="stHeader"], #MainMenu, footer {display:none;}

.stApp {
    background: linear-gradient(135deg, var(--bg-main), var(--bg-secondary));
    font-family: Arial, sans-serif;
}

[data-testid="stHeader"] {
    display: none !important;
    height: 0px !important;
}

[data-testid="block-container"],
[data-testid="stMainBlockContainer"] {
    max-width: 1400px;
    padding-top: 12px;
    padding-bottom: 0;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    max-width: 980px !important;
    margin: 10px auto 0 auto !important;
    border-radius: 18px !important;
    overflow: hidden !important;
    box-shadow: 0 25px 70px rgba(80, 70, 150, 0.15) ;
    border: 1px solid var(--border-soft) ;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 0px !important;
}

.left-panel,
.right-panel {
    min-height: auto;
}

.left-panel {
    padding: 0px 25px 10px 25px;
    text-align: center;
}

.right-panel {
    padding-top: 24px ;
}

.brand-row {
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
}

.brand-logo {
    width: 95px;
    height: 95px;
    object-fit: contain;
    margin-top: 6px;
    margin-right: -8px;
    margin-top: 0;
}

.brand-title {
    color: var(--purple-darkest);
    font-size: 42px;
    font-weight: 800;
}

.subtitle {
    color: var(--purple-darkest)  ; 
    font-size: 18px;
    margin: 4px auto 12px;
    text-align: center;
}

.features {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    text-align: left;
    font-size: 14px;
    color: var(--purple-darkest);
}

.feature {
    display: flex;
    gap: 10px;
    align-items: flex-start;
}

.feature-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
     background: var(--bg-card);
    color: var(--purple-primary);
    display: grid;
    place-items: center;
    font-weight: bold;
    box-shadow: var(--shadow-soft);
}

.form-title {
    text-align: center;
    margin-bottom: 18px;
}

.form-title h2 {
    color: var(--purple-darkest);
    font-size: 30px;
    margin-bottom: 8px;
}

.form-title p {
    color: var(--text-secondary);
    font-size: 17px;
}

.stButton > button {
    height: 60px;
    border-radius: 8px;
    font-weight: 700;
    border: 1px solid var(--border-primary);
}

.stButton > button[kind="primary"] {
     background: var(--bg-card);
    color: var(--purple-dark);
    border: 1px solid var(--purple-primary);
}

[data-testid="stTextInput"] label {
    color: var(--purple-darkest);
    font-weight: 700;
}

[data-testid="stTextInput"] input {
    height: 55px;
    border-radius: 8px;
}

[data-testid="stFormSubmitButton"] button {
    height: 58px;
    border-radius: 8px;
    border: none;
    color: white;
    font-weight: 800;
    background: linear-gradient(135deg, var(--purple-medium), var(--purple-dark));
}

.divider {
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 25px 0;
    color: var(--text-secondary);
}

.divider span {
    flex: 1;
    height: 1px;
    background: var(--border-primary);
}

.google-btn {
    width: 100%;
    height: 55px;
    border-radius: 8px;
     border: 1px solid var(--border-primary);
    background: var(--bg-card);
    font-weight: 700;
    color: var(--purple-darkest);
}

.signup {
    text-align: center;
    color: var(--text-secondary);
    margin-top: 25px;
}

.signup a {
    color: var(--purple-dark);
    font-weight: 800;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

with st.container(border=True):
    left, right = st.columns([0.8, 0.8], gap="xxsmall")

with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGO_PATH = BASE_DIR / "assets" / "logo.png"
    logo_base64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

    st.markdown(f"""
    <div class="brand-row">
    <img src="data:image/png;base64,{logo_base64}" class="brand-logo">
    <h1 class="brand-title">Quizy</h1>
    </div>
        <p class="subtitle">Votre assistant pédagogique intelligent</p>
    """, unsafe_allow_html=True)

    IMAGE_PATH = BASE_DIR / "assets" / "login.png"
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
