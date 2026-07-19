import streamlit as st
from pathlib import Path
import base64
from PIL import Image

BASE_DIR=Path(__file__).resolve().parent.parent

CSS_PATH = BASE_DIR / "assets" / "css" / "style.css"
LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"
ICONS_DIR = BASE_DIR / "assets" / "icons"

logo =Image.open(LOGO_PATH)

st.set_page_config(
    page_title= "Quizy | Documents",
    page_icon= logo,
    layout="wide",
    initial_sidebar_state="expanded",
)

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

def svg_button_icon(
    icon_name: str,
    alt_text: str = "Icon",
) -> str:
    svg = load_svg(icon_name)

    if not svg:
        return alt_text

    svg_base64 = base64.b64encode(
        svg.encode("utf-8")
    ).decode("utf-8")

    return (
        f"![{alt_text}]"
        f"(data:image/svg+xml;base64,{svg_base64})"
    )

def sidebar_item(
    label: str,
    icon_name: str,
    active: bool = False,
) -> str:
    icon = load_svg(icon_name)
    active_class = " active" if active else ""

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

    f'{sidebar_item("Dashboard", "dashboard.svg")}'
    f'{sidebar_item("Documents", "document.svg" , active=True)}'
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
# DOCUMENTS HEADER
# ==================================================

with st.container(key="documents-header"):

    title_col, search_col, upload_col = st.columns(
        [2.4, 1.15, 0.8],
        vertical_alignment="center",
    )

    with title_col:
        st.markdown(
            (
                '<div class="documents-title">'
                '<h1>My Documents</h1>'
                '<p>Upload, organize and manage your course materials.</p>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with search_col:
        search_query = st.text_input(
            "Search documents",
            placeholder="Search documents...",
            label_visibility="collapsed",
            key="documents-search",
        )

    with upload_col:
        upload_clicked = st.button(
            "＋ Upload Document",
            key="upload-document",
            use_container_width=True,
        )

    # ==================================================
    # DOCUMENTS
    # ==================================================

    documents = [
        {
            "Name": "Chapter 1 - Introduction.pdf",
            "Description": "Introduction aux systèmes informatiques",
            "Subject": "Computer Science",
            "Date": "20/07/2026",
            "Time": "10:30 AM",
            "Size": "2.4 MB",
            "Type": "PDF",
        },
        {
            "Name": "Algorithms.docx",
            "Description": "Structures de données et algorithmes",
            "Subject": "Algorithms",
            "Date": "18/07/2026",
            "Time": "2:15 PM",
            "Size": "1.8 MB",
            "Type": "DOCX",
        },
        {
            "Name": "Networks.pptx",
            "Description": "Réseaux informatiques",
            "Subject": "Networks",
            "Date": "15/07/2026",
            "Time": "9:45 AM",
            "Size": "5.6 MB",
            "Type": "PPTX",
        },
    ]

    view_icon = svg_button_icon("view.svg", "View")
    download_icon = svg_button_icon("download.svg", "Download")
    more_icon = svg_button_icon("menu.svg", "More")

    with st.container(key="documents-table"):

        # Toolbar
        toolbar_title, subject_filter, sort_filter, view_buttons = st.columns(
            [3.2, 1.1, 1.1, 0.8],
            vertical_alignment="center",
        )

        with toolbar_title:
            st.markdown(
                '<h2 class="documents-table-heading">All Documents</h2>',
                unsafe_allow_html=True,
            )

        with subject_filter:
            st.selectbox(
                "Subject",
                ["All Subjects", "Computer Science", "Algorithms", "Networks"],
                label_visibility="collapsed",
                key="subject-filter",
            )

        with sort_filter:
            st.selectbox(
                "Sort",
                ["Newest First", "Oldest First", "Name A-Z"],
                label_visibility="collapsed",
                key="sort-filter",
            )

        with view_buttons:
            list_col, grid_col = st.columns(2)

            with list_col:
                st.button(
                    "☰",
                    key="list-view",
                    use_container_width=True,
                )

            with grid_col:
                st.button(
                    "▦",
                    key="grid-view",
                    use_container_width=True,
                )

        # Column names
        header_cols = st.columns(
            [3.4, 1.45, 1.45, 0.8, 1.25],
            vertical_alignment="center",
        )

        headers = [
            "Document Name",
            "Subject",
            "Uploaded On",
            "Size",
            "Actions",
        ]

        for column, title in zip(header_cols, headers):
            column.markdown(
                f'<span class="table-column-title">{title}</span>',
                unsafe_allow_html=True,
            )

        # Rows
        for index, doc in enumerate(documents):
            with st.container(key=f"document-row-{index}"):
                name_col, subject_col, date_col, size_col, actions_col = st.columns(
                    [3.4, 1.45, 1.45, 0.8, 1.25],
                    vertical_alignment="center",
                )

                with name_col:
                    st.markdown(
                        (
                            '<div class="document-info">'
                            f'<div class="document-file-icon {doc["Type"].lower()}">'
                            f'{doc["Type"]}'
                            '</div>'
                            '<div class="document-text">'
                            f'<strong>{doc["Name"]}</strong>'
                            f'<small>{doc["Description"]}</small>'
                            '</div>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                with subject_col:
                    st.markdown(
                        f'<span class="subject-badge">{doc["Subject"]}</span>',
                        unsafe_allow_html=True,
                    )

                with date_col:
                    st.markdown(
                        (
                            '<div class="document-date">'
                            f'<span>{doc["Date"]}</span>'
                            f'<small>{doc["Time"]}</small>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                with size_col:
                    st.markdown(
                        f'<span class="document-size">{doc["Size"]}</span>',
                        unsafe_allow_html=True,
                    )

                with actions_col:
                    view_col, download_col, more_col = st.columns(3)

                    with view_col:
                        st.button(
                            view_icon,
                            key=f"view-{index}",
                            help="View document",
                            use_container_width=True,
                        )

                    with download_col:
                        st.button(
                            download_icon,
                            key=f"download-{index}",
                            help="Download document",
                            use_container_width=True,
                        )

                    with more_col:
                        st.button(
                            more_icon,
                            key=f"more-{index}",
                            help="More actions",
                            use_container_width=True,
                        )

        # Footer
        footer_text, pagination = st.columns(
            [4, 1],
            vertical_alignment="center",
        )

        with footer_text:
            st.markdown(
                '<p class="documents-count">Showing 1 to 3 of 12 documents</p>',
                unsafe_allow_html=True,
            )

        with pagination:
            previous, page1, page2, page3, next_page = st.columns(5)

            previous.button("‹", key="previous-page")
            page1.button("1", key="page-1", type="primary")
            page2.button("2", key="page-2")
            page3.button("3", key="page-3")
            next_page.button("›", key="next-page")