import sys
import mimetypes
from pathlib import Path

import streamlit as st
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from streamlit_cookies_controller import CookieController


# ==================================================
# ALLOW PYTHON TO FIND PROJECT FOLDERS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.database.connection import SessionLocal
from backend.services.document_service import (
    get_document_by_id,
)

from frontend.utils.auth_helpers import (
    require_role,
)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOGO_PATH = BASE_DIR / "assets" / "images" / "logo.png"

UPLOADS_DIR = PROJECT_ROOT / "uploads" / "documents"


# ==================================================
# PAGE CONFIG
# ==================================================

logo = Image.open(LOGO_PATH)

st.set_page_config(
    page_title="Quizy | Document Viewer",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================================================
# AUTHENTICATION
# ==================================================

cookie_controller = CookieController(
    key="document_viewer_cookie",
)

require_role(
    required_role="teacher",
    wrong_role_page="pages/student_dashboard.py",
)


# ==================================================
# GET DOCUMENT ID FROM URL
# ==================================================

document_id_value = st.query_params.get(
    "document_id"
)

if not document_id_value:
    st.error(
        "No document was selected."
    )
    st.stop()

try:
    document_id = int(document_id_value)

except ValueError:
    st.error(
        "Invalid document."
    )
    st.stop()


# ==================================================
# LOAD DOCUMENT FROM DATABASE
# ==================================================

try:
    with SessionLocal() as session:
        document = get_document_by_id(
            session=session,
            document_id=document_id,
        )

        if document is None:
            st.error(
                "Document not found."
            )
            st.stop()

        # Security check:
        # the document must belong to this teacher
        if (
            document.teacher_id
            != st.session_state["user_id"]
        ):
            st.error(
                "You do not have permission "
                "to view this document."
            )
            st.stop()

        document_title = document.title

        original_filename = (
            document.original_filename
        )

        file_path = document.file_path

        file_type = (
            document.file_type
            or Path(
                original_filename
            ).suffix.lstrip(".")
        ).upper()

        subject = document.subject or "Other"

except SQLAlchemyError as error:
    print(
        f"Document loading error: {error}"
    )

    st.error(
        "The document could not be loaded."
    )

    st.stop()


# ==================================================
# GET STORED FILE
# ==================================================

document_path = (
    PROJECT_ROOT / file_path
).resolve()

uploads_path = UPLOADS_DIR.resolve()

try:
    document_path.relative_to(
        uploads_path
    )

except ValueError:
    st.error(
        "Invalid document path."
    )
    st.stop()


if not document_path.is_file():
    st.error(
        "The document file could not be found."
    )
    st.stop()


# ==================================================
# DOCUMENT HEADER
# ==================================================

st.title(document_title)

st.caption(
    f"{subject} • {file_type} • "
    f"{original_filename}"
)

st.divider()


# ==================================================
# PDF VIEWER
# ==================================================

if file_type == "PDF":
    st.pdf(
        document_path,
        height=850,
    )


# ==================================================
# OTHER FILE TYPES
# ==================================================

else:
    st.info(
        f"Preview is not available for "
        f"{file_type} documents yet."
    )

    mime_type = (
        mimetypes.guess_type(
            original_filename
        )[0]
        or "application/octet-stream"
    )

    st.download_button(
        "Download document",
        data=document_path.read_bytes(),
        file_name=original_filename,
        mime=mime_type,
    )