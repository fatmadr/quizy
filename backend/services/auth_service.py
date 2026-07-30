
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import User
from backend.security.passwords import (
    hash_password,
    validate_password,
    verify_and_update_password,
    verify_password,
)
from backend.services.user_service import (
    create_user,
    get_user_by_email,
)

# ==================================================
# REGISTER USER
# ==================================================

def register_user(
    session: Session,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role: str,
) -> User:
    validate_password(password)

    password_hash = hash_password(password)

    return create_user(
        session=session,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash,
        role=role,
    )


# ==================================================
# AUTHENTICATE USER
# ==================================================

def authenticate_user(
    session: Session,
    email: str,
    password: str,
) -> User | None:
    if not isinstance(email, str):
        return None

    if not isinstance(password, str):
        return None

    normalized_email = email.strip().lower()

    if not normalized_email or not password:
        return None

    user = get_user_by_email(
        session=session,
        email=normalized_email,
    )

    if user is None:
        return None

    password_is_valid, updated_hash = (
        verify_and_update_password(
            plain_password=password,
            stored_password_hash=user.password_hash,
        )
    )

    if not password_is_valid:
        return None

    if updated_hash is not None:
        try:
            user.password_hash = updated_hash
            session.commit()
            session.refresh(user)

        except SQLAlchemyError:
            session.rollback()
            raise

    return user


# ==================================================
# CHANGE PASSWORD
# ==================================================

def change_password(
    session: Session,
    user_id: int,
    current_password: str,
    new_password: str,
) -> bool:
    user = session.get(User, user_id)

    if user is None:
        return False

    current_password_is_valid = verify_password(
        plain_password=current_password,
        stored_password_hash=user.password_hash,
    )

    if not current_password_is_valid:
        raise ValueError(
            "The current password is incorrect."
        )

    validate_password(new_password)

    if current_password == new_password:
        raise ValueError(
            "The new password must be different "
            "from the current password."
        )

    new_password_hash = hash_password(new_password)

    try:
        user.password_hash = new_password_hash

        session.commit()
        session.refresh(user)

        return True

    except SQLAlchemyError:
        session.rollback()
        raise