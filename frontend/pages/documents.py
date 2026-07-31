import base64
import sys
from html import escape
from uuid import uuid4
from pathlib import Path
import mimetypes

import streamlit as st
from PIL import Image
from math import ceil
from streamlit_cookies_controller import CookieController
from sqlalchemy.exc import SQLAlchemyError

# ==================================================
# ALLOW PYTHON TO FIND PROJECT FOLDERS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.connection import SessionLocal
from backend.services.document_service import (
    create_document,
    get_documents_by_teacher,
)

from frontend.components.sidebar import build_teacher_sidebar
from frontend.utils.auth_helpers import (
    get_current_user_name,
    logout_user,
    require_role,
)


BASE_DIR=Path(__file__).resolve().parent.parent

CSS_PATH = BASE_DIR / "assets" / "css" / "style.css"
LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"
ICONS_DIR = BASE_DIR / "assets" / "icons"

UPLOADS_DIR = PROJECT_ROOT / "uploads" / "documents"

ALLOWED_FILE_TYPES = {
    ".pdf",
    ".docx",
    ".pptx",
}

logo =Image.open(LOGO_PATH)

st.set_page_config(
    page_title= "Quizy | Documents",
    page_icon= logo,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# RESTORE LOGIN AFTER REFRESH
# ==================================================

COOKIE_NAME = "quizy_session"

cookie_controller = CookieController(
    key="documents_cookie",
)

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

if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False

if "documents_page" not in st.session_state:
    st.session_state.documents_page = 1

def reset_documents_page() -> None:
    st.session_state.documents_page = 1

upload_message = st.session_state.pop(
    "document_upload_message",
    None,
)

if upload_message:
    st.success(upload_message)


css = CSS_PATH.read_text(encoding="utf-8")

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True,
)

def format_file_size(
    file_size_bytes: int | None,
) -> str:
    if file_size_bytes is None:
        return "-"

    if file_size_bytes < 1024:
        return f"{file_size_bytes} B"

    if file_size_bytes < 1024 * 1024:
        return f"{file_size_bytes / 1024:.1f} KB"

    return (
        f"{file_size_bytes / (1024 * 1024):.1f} MB"
    )

def get_document_path(
    relative_file_path: str,
) -> Path | None:
    document_path = (
        PROJECT_ROOT / relative_file_path
    ).resolve()

    uploads_path = UPLOADS_DIR.resolve()

    # Prevent access to files outside uploads/documents
    try:
        document_path.relative_to(uploads_path)
    except ValueError:
        return None

    if not document_path.is_file():
        return None

    return document_path

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



# ==================================================
# SIDEBAR
# ==================================================
sidebar_html = build_teacher_sidebar(
    logo_path=LOGO_PATH,
    icons_dir=ICONS_DIR,
    teacher_name=teacher_name,
    active_page="documents",
)

# ==================================================
# DISPLAY SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown(
        sidebar_html,
        unsafe_allow_html=True,
    )

    if st.button(
        "↪ Logout",
        key="documents_logout",
        use_container_width=True,
    ):
        logout_user(cookie_controller)

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
            on_change=reset_documents_page,
        )

    with upload_col:
        upload_clicked = st.button(
            "＋ Upload Document",
            key="upload-document",
            use_container_width=True,
        )
    if upload_clicked:
        st.session_state.show_upload_form = (
            not st.session_state.show_upload_form
        )

    if st.session_state.show_upload_form:
        with st.form(
                "upload_document_form",
                clear_on_submit=True,
        ):
            st.markdown("### Upload a new document")

            document_title = st.text_input(
                "Document title",
                placeholder=(
                    "Leave empty to use the filename"
                ),
            )

            document_subject = st.selectbox(
                "Subject",
                [
                    "Computer Science",
                    "Algorithms",
                    "Networks",
                    "Databases",
                    "Artificial Intelligence",
                    "Other",
                ],
            )

            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "docx", "pptx"],
            )

            upload_submitted = st.form_submit_button(
                "Save Document",
                use_container_width=True,
            )

        if upload_submitted:
            if uploaded_file is None:
                st.error("Please select a document.")

            else:
                saved_path = None

                try:
                    original_filename = Path(
                        uploaded_file.name
                    ).name

                    file_extension = Path(
                        original_filename
                    ).suffix.lower()

                    if file_extension not in ALLOWED_FILE_TYPES:
                        raise ValueError(
                            "Only PDF, DOCX, and PPTX "
                            "files are allowed."
                        )

                    teacher_id = st.session_state["user_id"]

                    teacher_upload_dir = (
                            UPLOADS_DIR / str(teacher_id)
                    )

                    teacher_upload_dir.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    stored_filename = (
                        f"{uuid4().hex}{file_extension}"
                    )

                    saved_path = (
                            teacher_upload_dir
                            / stored_filename
                    )

                    saved_path.write_bytes(
                        uploaded_file.getvalue()
                    )

                    cleaned_title = document_title.strip()

                    if not cleaned_title:
                        cleaned_title = Path(
                            original_filename
                        ).stem

                    relative_file_path = (
                        saved_path
                        .relative_to(PROJECT_ROOT)
                        .as_posix()
                    )

                    with SessionLocal() as session:
                        create_document(
                            session=session,
                            teacher_id=teacher_id,
                            title=cleaned_title,
                            original_filename=(
                                original_filename
                            ),
                            file_path=relative_file_path,
                            subject=document_subject,
                            file_type=(
                                file_extension
                                .lstrip(".")
                                .upper()
                            ),
                            file_size_bytes=(
                                uploaded_file.size
                            ),
                        )

                    st.session_state.show_upload_form = False

                    st.session_state.document_upload_message = (
                        "Document uploaded successfully."
                    )

                    st.rerun()

                except ValueError as error:
                    if (
                            saved_path is not None
                            and saved_path.exists()
                    ):
                        saved_path.unlink()

                    st.error(str(error))

                except (OSError, SQLAlchemyError) as error:
                    if (
                            saved_path is not None
                            and saved_path.exists()
                    ):
                        saved_path.unlink()

                    print(
                        f"Document upload error: {error}"
                    )

                    st.error(
                        "The document could not be uploaded."
                    )

    # ==================================================
    # DOCUMENTS
    # ==================================================
    # ==================================================
    # LOAD TEACHER DOCUMENTS
    # ==================================================

    try:
        with SessionLocal() as session:
            database_documents = get_documents_by_teacher(
                session=session,
                teacher_id=st.session_state["user_id"],
            )

            documents = []

            for document in database_documents:
                uploaded_at = document.uploaded_at

                document_type = (
                        document.file_type
                        or Path(
                    document.original_filename
                ).suffix.lstrip(".")
                        or "FILE"
                ).upper()

                documents.append(
                    {
                        "Id": document.document_id,
                        "Name": document.title,
                        "Description": (
                            document.original_filename
                        ),
                        "Subject": document.subject or "Other",
                        "Type": document_type,
                        "Date": (
                            uploaded_at.strftime(
                                "%d/%m/%Y"
                            )
                            if uploaded_at
                            else "-"
                        ),
                        "Time": (
                            uploaded_at.strftime(
                                "%I:%M %p"
                            )
                            if uploaded_at
                            else ""
                        ),
                        "Size": format_file_size(
                            document.file_size_bytes
                        ),
                        "UploadedAt": uploaded_at,
                        "FilePath": document.file_path,
                    }
                )

    except SQLAlchemyError as error:
        print(f"Document loading error: {error}")

        st.error(
            "The documents could not be loaded."
        )

        documents = []
    view_icon = svg_button_icon("view.svg", "View")
    download_icon = svg_button_icon("download.svg", "Download")
    more_icon = svg_button_icon("menu.svg", "More")

    with st.container(key="documents-table"):

        # Toolbar
        (
            toolbar_title,
            subject_filter,
            sort_filter,
            page_size_filter,
            view_buttons,
        ) = st.columns(
            [2.6, 1.2, 1.2, 1.0, 0.8],
            vertical_alignment="center",
        )

        with toolbar_title:
            st.markdown(
                '<h2 class="documents-table-heading">All Documents</h2>',
                unsafe_allow_html=True,
            )

        with subject_filter:
            subject_options = ["All Subjects"] + sorted(
                {
                    document["Subject"]
                    for document in documents
                    if document.get("Subject")
                }
            )

            selected_subject = st.selectbox(
                "Subject",
                subject_options,
                label_visibility="collapsed",
                key="subject-filter",
                on_change=reset_documents_page,
            )

        with sort_filter:
            sort_order = st.selectbox(
                "Sort",
                [
                    "Newest First",
                    "Oldest First",
                    "Name A-Z",
                ],
                label_visibility="collapsed",
                key="sort-filter",
                on_change=reset_documents_page,
            )

        with page_size_filter:
            page_size = st.selectbox(
                "Documents per page",
                [5, 10],
                index=1,
                format_func=lambda value: f"{value} per page",
                label_visibility="collapsed",
                key="documents-page-size",
                on_change=reset_documents_page,
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

        # ==================================================
        # SEARCH, FILTER AND SORT
        # ==================================================

        displayed_documents = documents.copy()

        normalized_search = search_query.strip().lower()

        if normalized_search:
            displayed_documents = [
                document
                for document in displayed_documents
                if (
                        normalized_search
                        in document["Name"].lower()
                        or normalized_search
                        in document["Description"].lower()
                )
            ]

        if selected_subject != "All Subjects":
            displayed_documents = [
                document
                for document in displayed_documents
                if document.get("Subject") == selected_subject
            ]

        if sort_order == "Oldest First":
            displayed_documents.sort(
                key=lambda document: (
                    document["UploadedAt"] is None,
                    document["UploadedAt"],
                )
            )

        elif sort_order == "Name A-Z":
            displayed_documents.sort(
                key=lambda document: document["Name"].lower()
            )

        else:
            displayed_documents.sort(
                key=lambda document: (
                    document["UploadedAt"] is not None,
                    document["UploadedAt"],
                ),
                reverse=True,
            )

        # ==================================================
        # PAGINATION
        # ==================================================

        total_documents = len(displayed_documents)

        total_pages = (
            ceil(total_documents / page_size)
            if total_documents > 0
            else 0
        )

        if total_pages == 0:
            st.session_state.documents_page = 1

            current_page = 1
            start_index = 0
            end_index = 0
            page_documents = []

        else:
            current_page = min(
                max(st.session_state.documents_page, 1),
                total_pages,
            )

            st.session_state.documents_page = current_page

            start_index = (
                                  current_page - 1
                          ) * page_size

            end_index = min(
                start_index + page_size,
                total_documents,
            )

            page_documents = displayed_documents[
                start_index:end_index
            ]

        # Column names
        header_cols = st.columns(
            [2.8, 1.3, 0.7, 1.35, 0.75, 1.2],
            vertical_alignment="center",
        )

        headers = [
            "Document Name",
            "Subject",
            "Type",
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
        for index, doc in enumerate(
                page_documents,
                start=start_index,
        ):
            document_path = get_document_path(
                doc["FilePath"]
            )

            mime_type = (
                    mimetypes.guess_type(
                        doc["Description"]
                    )[0]
                    or "application/octet-stream"
            )

            with st.container(key=f"document-row-{index}"):
                (
                    name_col,
                    subject_col,
                    type_col,
                    date_col,
                    size_col,
                    actions_col,
                ) = st.columns(
                    [2.8, 1.3, 0.7, 1.35, 0.75, 1.2],
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

                with type_col:
                    st.markdown(
                        f'<span class="document-type">{doc["Type"]}</span>',
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
                            key=f'view-{doc["Id"]}',
                            help="View document",
                            use_container_width=True,
                        )

                    with download_col:
                        if document_path is not None:
                            st.download_button(
                                label=download_icon,
                                data=document_path.read_bytes(),
                                file_name=doc["Description"],
                                mime=mime_type,
                                key=f'download-{doc["Id"]}',
                                help="Download document",
                                use_container_width=True,
                            )

                        else:
                            st.button(
                                download_icon,
                                key=f'missing-download-{doc["Id"]}',
                                help="The stored file could not be found",
                                disabled=True,
                                use_container_width=True,
                            )

                    with more_col:
                        st.button(
                            more_icon,
                            key=f'more-{doc["Id"]}',
                            help="More actions",
                            use_container_width=True,
                        )

        # Footer
        footer_text, pagination = st.columns(
            [4, 1],
            vertical_alignment="center",
        )

    with footer_text:
        if total_documents == 0:
            count_text = "Showing 0 of 0 documents"

        else:
            count_text = (
                f"Showing {start_index + 1} "
                f"to {end_index} "
                f"of {total_documents} documents"
            )

        st.markdown(
            (
                '<p class="documents-count">'
                f'{count_text}'
                '</p>'
            ),
            unsafe_allow_html=True,
        )

    with pagination:
        if total_pages > 1:
            pagination_columns = st.columns(
                total_pages + 2
            )

            previous_clicked = pagination_columns[0].button(
                "‹",
                key="previous-page",
                disabled=current_page == 1,
                use_container_width=True,
            )

            if previous_clicked:
                st.session_state.documents_page -= 1
                st.rerun()

            for page_number in range(
                    1,
                    total_pages + 1,
            ):
                page_clicked = pagination_columns[
                    page_number
                ].button(
                    str(page_number),
                    key=f"page-{page_number}",
                    type=(
                        "primary"
                        if page_number == current_page
                        else "secondary"
                    ),
                    use_container_width=True,
                )

                if page_clicked:
                    st.session_state.documents_page = (
                        page_number
                    )
                    st.rerun()

            next_clicked = pagination_columns[-1].button(
                "›",
                key="next-page",
                disabled=current_page == total_pages,
                use_container_width=True,
            )

            if next_clicked:
                st.session_state.documents_page += 1
                st.rerun()

