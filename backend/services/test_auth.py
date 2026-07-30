from sqlalchemy import select

from backend.database.connection import SessionLocal
from backend.models import User
from backend.services.auth_session_service import (
    create_auth_session,
    delete_auth_session,
    get_user_from_token,
)


def run_test() -> None:
    with SessionLocal() as session:
        user = session.scalar(
            select(User).limit(1)
        )

        if user is None:
            raise RuntimeError(
                "No user exists. Create an account first."
            )

        # Create a persistent authentication session
        token = create_auth_session(
            session=session,
            user_id=user.user_id,
        )

        print("Authentication session created.")

        # Try to restore the user from the token
        restored_user = get_user_from_token(
            session=session,
            token=token,
        )

        if restored_user is None:
            raise RuntimeError(
                "The user could not be restored."
            )

        if restored_user.user_id != user.user_id:
            raise RuntimeError(
                "The restored user is incorrect."
            )

        print(
            "User restored successfully:",
            restored_user.email,
        )

        # Simulate Logout
        deleted = delete_auth_session(
            session=session,
            token=token,
        )

        if not deleted:
            raise RuntimeError(
                "The authentication session "
                "was not deleted."
            )

        print("Authentication session deleted.")

        # The token should no longer work
        user_after_logout = get_user_from_token(
            session=session,
            token=token,
        )

        if user_after_logout is not None:
            raise RuntimeError(
                "The token still works after logout."
            )

        print("Old token correctly rejected.")
        print("Auth-session service test passed!")


if __name__ == "__main__":
    run_test()