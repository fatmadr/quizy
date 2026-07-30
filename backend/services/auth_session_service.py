import hashlib
import secrets

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import AuthSession, User


# ==================================================
# TOKEN HASHING
# ==================================================

def hash_session_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ==================================================
# CREATE AUTHENTICATION SESSION
# ==================================================

def create_auth_session(
    session: Session,
    user_id: int,
) -> str:
    # This original token will be stored in the cookie.
    token = secrets.token_urlsafe(32)

    # Only its hash is stored in PostgreSQL.
    token_hash = hash_session_token(token)

    auth_session = AuthSession(
        user_id=user_id,
        token_hash=token_hash,
    )

    try:
        session.add(auth_session)
        session.commit()

        return token

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# FIND USER USING TOKEN
# ==================================================

def get_user_from_token(
    session: Session,
    token: str | None,
) -> User | None:
    if not token:
        return None

    token_hash = hash_session_token(token)

    statement = (
        select(User)
        .join(
            AuthSession,
            AuthSession.user_id == User.user_id,
        )
        .where(
            AuthSession.token_hash == token_hash
        )
    )

    return session.scalar(statement)


# ==================================================
# DELETE CURRENT SESSION
# ==================================================

def delete_auth_session(
    session: Session,
    token: str | None,
) -> bool:
    if not token:
        return False

    token_hash = hash_session_token(token)

    statement = delete(AuthSession).where(
        AuthSession.token_hash == token_hash
    )

    try:
        result = session.execute(statement)
        session.commit()

        return result.rowcount > 0

    except SQLAlchemyError:
        session.rollback()
        raise