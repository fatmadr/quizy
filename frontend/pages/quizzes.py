import sys
from pathlib import Path

import streamlit as st
import time
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from streamlit_cookies_controller import (
    CookieController,
)


# ==================================================
# PROJECT ROOT
# ==================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ==================================================
# PROJECT IMPORTS
# ==================================================

from backend.database.connection import (
    SessionLocal,
)

from backend.services.document_service import (
    get_document_by_id,
    get_documents_by_teacher,
)

from backend.services.text_chunk_service import (
    split_text_into_chunks,
)

from backend.services.embedding_service import (
    create_embeddings,
)

from backend.services.retrieval_service import (
    retrieve_relevant_chunks,
)

from backend.services.document_text_service import (
    extract_document_text,
)

from backend.services.quiz_service import (
    create_quiz_draft,
    get_quizzes_by_teacher,
)

from frontend.components.sidebar import (
    build_teacher_sidebar,
)

from frontend.utils.auth_helpers import (
    get_current_user_name,
    logout_user,
    require_role,
)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

CSS_PATH = (
    BASE_DIR
    / "assets"
    / "css"
    / "style.css"
)

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "images"
    / "logo.png"
)

ICONS_DIR = (
    BASE_DIR
    / "assets"
    / "icons"
)


# ==================================================
# PAGE CONFIG
# ==================================================

logo = Image.open(LOGO_PATH)

st.set_page_config(
    page_title="Quizy | Quizzes",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# AUTH
# ==================================================

cookie_controller = CookieController(
    key="quizzes_cookie",
)

require_role(
    required_role="teacher",
    wrong_role_page="pages/student_dashboard.py",
)

teacher_name = get_current_user_name(
    default_name="Teacher",
)

quiz_message = st.session_state.pop(
    "quiz_message",
    None,
)

if quiz_message:
    st.success(quiz_message)


# ==================================================
# CSS
# ==================================================

css = CSS_PATH.read_text(
    encoding="utf-8"
)

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
    active_page="quizzes",
)

with st.sidebar:
    st.markdown(
        sidebar_html,
        unsafe_allow_html=True,
    )

    if st.button(
        "↪ Logout",
        key="quizzes_logout",
        use_container_width=True,
    ):
        logout_user(
            cookie_controller
        )


# ==================================================
# LOAD DOCUMENTS
# ==================================================

try:
    with SessionLocal() as session:
        teacher_documents = get_documents_by_teacher(
            session=session,
            teacher_id=st.session_state["user_id"],
        )

        document_options = {
            document.title: document.document_id
            for document in teacher_documents
        }

except SQLAlchemyError as error:
    print(
        f"Document loading error: {error}"
    )

    document_options = {}

    st.error(
        "Documents could not be loaded."
    )

    # ==================================================
    # PREPROCESS DOCUMENT
    # ==================================================


def preprocess_document(
        document_id: int,
        document_path: Path,
):
    cache_key = (
        f"document_ai_{document_id}"
    )

    if cache_key in st.session_state:
        print(
            "Using cached document embeddings."
        )

        return st.session_state[
            cache_key
        ]

    print(
        "Processing document for the first time..."
    )

    extracted_text = extract_document_text(
        document_path
    )

    chunks = split_text_into_chunks(
        extracted_text
    )

    embeddings = create_embeddings(
        chunks
    )

    result = {
        "text": extracted_text,
        "chunks": chunks,
        "embeddings": embeddings,
    }

    st.session_state[
        cache_key
    ] = result

    return result


# ==================================================
# QUIZZES PAGE CONTENT
# ==================================================

st.title("My Quizzes")

st.caption(
    "Create and manage quizzes "
    "from your course documents."
)


# ==================================================
# CREATE QUIZ FORM
# ==================================================

if not document_options:
    st.info(
        "Upload a document before "
        "creating a quiz."
    )

else:
    with st.form(
        "create_quiz_form"
    ):
        selected_document = st.selectbox(
            "Source document",
            list(
                document_options.keys()
            ),
        )

        quiz_title = st.text_input(
            "Quiz title",
            placeholder=(
                "Example: Algorithms Quiz"
            ),
        )

        quiz_description = st.text_area(
            "Description",
            placeholder=(
                "Optional description"
            ),
        )

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard",
            ],
        )

        use_time_limit = st.checkbox(
            "Add time limit"
        )

        time_limit = None

        if use_time_limit:
            time_limit = st.number_input(
                "Time limit (minutes)",
                min_value=1,
                value=20,
                step=1,
            )

        create_clicked = st.form_submit_button(
            "Generate Quiz",
            use_container_width=True,
        )

        # ==================================================
        # GENERATE QUIZ
        # ==================================================

        if create_clicked:
            try:
                document_id = document_options[
                    selected_document
                ]

                # ==========================================
                # GET SELECTED DOCUMENT
                # ==========================================

                with SessionLocal() as session:
                    document = get_document_by_id(
                        session=session,
                        document_id=document_id,
                    )

                    if document is None:
                        raise ValueError(
                            "Document not found."
                        )

                    if (
                            document.teacher_id
                            != st.session_state["user_id"]
                    ):
                        raise ValueError(
                            "You do not have permission "
                            "to use this document."
                        )

                    document_file_path = (
                        document.file_path
                    )

                # ==========================================
                # GET REAL FILE PATH
                # ==========================================

                document_path = (
                        PROJECT_ROOT
                        / document_file_path
                ).resolve()

                # ==========================================
                # PREPROCESS DOCUMENT
                # ==========================================

                start_time = time.perf_counter()

                processed_document = preprocess_document(
                    document_id=document_id,
                    document_path=document_path,
                )

                print(
                    "Document preprocessing:",
                    round(
                        time.perf_counter()
                        - start_time,
                        2,
                    ),
                    "seconds",
                )

                extracted_text = processed_document[
                    "text"
                ]

                chunks = processed_document[
                    "chunks"
                ]

                embeddings = processed_document[
                    "embeddings"
                ]

                print(
                    "Extracted characters:",
                    len(extracted_text),
                )

                print(
                    "Number of chunks:",
                    len(chunks),
                )

                print(
                    "Number of embeddings:",
                    len(embeddings),
                )

                if embeddings:
                    print(
                        "Embedding dimensions:",
                        len(embeddings[0]),
                    )

                # ==========================================
                # RETRIEVAL QUERY
                # ==========================================

                retrieval_query = (
                    f"Important concepts, definitions, "
                    f"explanations and exercises suitable "
                    f"for a {difficulty.lower()} quiz "
                    f"based on this course document."
                )

                # ==========================================
                # QUERY EMBEDDING
                # ==========================================

                start_time = time.perf_counter()

                query_embedding = create_embeddings(
                    [retrieval_query]
                )[0]

                print(
                    "Query embedding:",
                    round(
                        time.perf_counter()
                        - start_time,
                        2,
                    ),
                    "seconds",
                )

                # ==========================================
                # RETRIEVE RELEVANT CHUNKS
                # ==========================================

                start_time = time.perf_counter()

                relevant_chunks = retrieve_relevant_chunks(
                    chunks=chunks,
                    chunk_embeddings=embeddings,
                    query_embedding=query_embedding,
                    top_k=min(
                        5,
                        len(chunks),
                    ),
                )

                print(
                    "Retrieval:",
                    round(
                        time.perf_counter()
                        - start_time,
                        2,
                    ),
                    "seconds",
                )

                print(
                    "Relevant chunks:",
                    len(relevant_chunks),
                )

                for index, chunk in enumerate(
                        relevant_chunks,
                        start=1,
                ):
                    print(
                        f"\n--- Relevant Chunk {index} ---"
                    )

                    print(
                        chunk[:500]
                    )

                # ==========================================
                # CREATE QUIZ DRAFT
                # ==========================================

                with SessionLocal() as session:
                    quiz = create_quiz_draft(
                        session=session,
                        teacher_id=st.session_state[
                            "user_id"
                        ],
                        document_id=document_id,
                        title=quiz_title,
                        description=quiz_description,
                        difficulty=difficulty.lower(),
                        time_limit_minutes=(
                            int(time_limit)
                            if time_limit is not None
                            else None
                        ),
                    )

                st.session_state[
                    "quiz_message"
                ] = (
                    f'Quiz "{quiz.title}" '
                    f'created successfully.'
                )

                st.rerun()

            except (
                    ValueError,
                    FileNotFoundError,
                    RuntimeError,
            ) as error:
                st.error(
                    str(error)
                )

            except SQLAlchemyError as error:
                print(
                    f"Quiz creation error: {error}"
                )

                st.error(
                    "The quiz could not be created."
                )

    # ==================================================
    # LOAD TEACHER QUIZZES
    # ==================================================

try:
    with SessionLocal() as session:
        quizzes = get_quizzes_by_teacher(
            session=session,
            teacher_id=st.session_state[
                "user_id"
            ],
        )

except SQLAlchemyError as error:
    print(
        f"Quiz loading error: {error}"
    )

    quizzes = []

    st.error(
        "The quizzes could not be loaded."
    )

    # ==================================================
    # ALL QUIZZES
    # ==================================================

st.markdown("## All Quizzes")

if not quizzes:
    st.info(
        "You haven't created any quizzes yet."
    )

else:
    for quiz in quizzes:
        with st.container(
                key=f"quiz-{quiz.quiz_id}"
        ):
            title_col, info_col = st.columns(
                [2.5, 1.5],
                vertical_alignment="center",
            )

            with title_col:
                st.markdown(
                    f"### {quiz.title}"
                )

                st.caption(
                    f"Source: "
                    f"{quiz.document.title}"
                )

            with info_col:
                st.write(
                    f"**Difficulty:** "
                    f"{quiz.difficulty.title()}"
                )

                st.write(
                    f"**Status:** "
                    f"{quiz.status.title()}"
                )

                if quiz.time_limit_minutes:
                    st.write(
                        f"**Time limit:** "
                        f"{quiz.time_limit_minutes} min"
                    )

                else:
                    st.write(
                        "**Time limit:** None"
                    )

            st.divider()