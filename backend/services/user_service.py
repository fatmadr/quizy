from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import User


VALID_ROLES = {"teacher", "student"}


# ==================================================
# GET USER BY ID
# ==================================================

def get_user_by_id(
    session: Session,
    user_id: int,
) -> User | None:
    return session.get(User, user_id)


# ==================================================
# GET USER BY EMAIL
# ==================================================

def get_user_by_email(
    session: Session,
    email: str,
) -> User | None:
    normalized_email = email.strip().lower()

    statement = select(User).where(
        User.email == normalized_email
    )

    return session.scalar(statement)


# ==================================================
# GET ALL USERS
# ==================================================

def get_all_users(
    session: Session,
) -> list[User]:
    statement = select(User).order_by(User.user_id)

    return list(session.scalars(statement).all())


# ==================================================
# CREATE USER
# ==================================================

def create_user(
    session: Session,
    first_name: str,
    last_name: str,
    email: str,
    password_hash: str,
    role: str,
) -> User:
    normalized_email = email.strip().lower()
    normalized_role = role.strip().lower()

    if not first_name.strip():
        raise ValueError("First name is required.")

    if not last_name.strip():
        raise ValueError("Last name is required.")

    if not normalized_email:
        raise ValueError("Email is required.")

    if not password_hash:
        raise ValueError("Password hash is required.")

    if normalized_role not in VALID_ROLES:
        raise ValueError(
            "Role must be either 'teacher' or 'student'."
        )

    existing_user = get_user_by_email(
        session=session,
        email=normalized_email,
    )

    if existing_user is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    new_user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=normalized_email,
        password_hash=password_hash,
        role=normalized_role,
    )

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return new_user

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# DELETE USER
# ==================================================

def delete_user(
    session: Session,
    user_id: int,
) -> bool:
    user = session.get(User, user_id)

    if user is None:
        return False

    try:
        session.delete(user)
        session.commit()

        return True

    except SQLAlchemyError:
        session.rollback()
        raise