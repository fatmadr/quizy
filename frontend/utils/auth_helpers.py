from html import escape

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from streamlit_cookies_controller import CookieController

from backend.database.connection import SessionLocal
from backend.services.auth_session_service import (
    delete_auth_session,
    get_user_from_token,
)


COOKIE_NAME = "quizy_session"


# ==================================================
# RESTORE LOGIN FROM COOKIE
# ==================================================

def restore_login_from_cookie() -> None:
    if st.session_state.get("logged_in", False):
        return

    session_token = st.context.cookies.get(
        COOKIE_NAME
    )

    if not session_token:
        return

    try:
        with SessionLocal() as session:
            user = get_user_from_token(
                session=session,
                token=session_token,
            )

            if user is None:
                return

            user_data = {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
            }

        st.session_state.logged_in = True
        st.session_state.user_id = user_data["user_id"]
        st.session_state.first_name = user_data["first_name"]
        st.session_state.last_name = user_data["last_name"]
        st.session_state.email = user_data["email"]
        st.session_state.role = user_data["role"]

    except SQLAlchemyError as error:
        print(f"Session restoration error: {error}")


# ==================================================
# PROTECT PAGE
# ==================================================

def require_role(
    required_role: str,
    wrong_role_page: str,
) -> None:
    restore_login_from_cookie()

    if not st.session_state.get("logged_in", False):
        st.switch_page("app.py")

    if st.session_state.get("role") != required_role:
        st.switch_page(wrong_role_page)


# ==================================================
# CURRENT USER NAME
# ==================================================

def get_current_user_name(
    default_name: str = "User",
) -> str:
    first_name = (
        st.session_state.get("first_name")
        or default_name
    )

    last_name = (
        st.session_state.get("last_name")
        or ""
    )

    return escape(
        f"{first_name} {last_name}".strip()
    )


# ==================================================
# LOGOUT
# ==================================================

def logout_user(
    cookie_controller: CookieController,
) -> None:
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
            print(f"Logout database error: {error}")

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