from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


# ==================================================
# PASSWORD HASHER
# ==================================================

password_hasher = PasswordHash.recommended()


# ==================================================
# PASSWORD VALIDATION
# ==================================================

def validate_password(password: str) -> None:
    if not isinstance(password, str):
        raise ValueError("Password must be text.")

    if not password:
        raise ValueError("Password is required.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    if len(password) > 128:
        raise ValueError(
            "Password cannot exceed 128 characters."
        )


# ==================================================
# HASH PASSWORD
# ==================================================

def hash_password(password: str) -> str:
    validate_password(password)

    return password_hasher.hash(password)


# ==================================================
# VERIFY PASSWORD
# ==================================================

def verify_password(
    plain_password: str,
    stored_password_hash: str,
) -> bool:
    if not plain_password or not stored_password_hash:
        return False

    try:
        return password_hasher.verify(
            plain_password,
            stored_password_hash,
        )

    except UnknownHashError:
        return False


# ==================================================
# VERIFY AND UPGRADE HASH
# ==================================================

def verify_and_update_password(
    plain_password: str,
    stored_password_hash: str,
) -> tuple[bool, str | None]:
    if not plain_password or not stored_password_hash:
        return False, None

    try:
        return password_hasher.verify_and_update(
            plain_password,
            stored_password_hash,
        )

    except UnknownHashError:
        return False, None