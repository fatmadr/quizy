import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# ==================================================
# LOCATE AND LOAD THE .env FILE
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ==================================================
# READ DATABASE INFORMATION FROM .env
# ==================================================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


# Check that the important values exist
required_values = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
}

missing_values = [
    name
    for name, value in required_values.items()
    if not value
]

if missing_values:
    raise RuntimeError(
        "Missing values in .env: "
        + ", ".join(missing_values)
    )


# ==================================================
# CREATE THE POSTGRESQL ADDRESS
# ==================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# ==================================================
# CREATE THE SQLALCHEMY ENGINE
# ==================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ==================================================
# TEST THE DATABASE CONNECTION
# ==================================================

def test_connection() -> None:
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database();")
            ).scalar_one()

        print("Database connection successful!")
        print(f"Connected to: {database_name}")

    except Exception as error:
        print("Database connection failed.")
        print(f"Error: {error}")


if __name__ == "__main__":
    test_connection()