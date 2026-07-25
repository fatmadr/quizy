from sqlalchemy import func, inspect, select
from sqlalchemy.exc import SQLAlchemyError

from backend.database.connection import SessionLocal, engine
from backend.models import (
    Document,
    Question,
    QuestionOption,
    Quiz,
    QuizAttempt,
    StudentAnswer,
    User,
)


EXPECTED_TABLES = {
    "users",
    "documents",
    "quizzes",
    "questions",
    "question_options",
    "quiz_attempts",
    "student_answers",
}


def check_tables() -> None:
    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names(schema="public")
    )

    missing_tables = EXPECTED_TABLES - existing_tables

    print("Existing tables:")

    for table_name in sorted(existing_tables):
        print(f"- {table_name}")

    if missing_tables:
        print("\nMissing tables:")

        for table_name in sorted(missing_tables):
            print(f"- {table_name}")

        raise RuntimeError(
            "Some required database tables are missing."
        )

    print("\nAll required tables exist.")


def check_model_queries() -> None:
    models = [
        User,
        Document,
        Quiz,
        Question,
        QuestionOption,
        QuizAttempt,
        StudentAnswer,
    ]

    with SessionLocal() as session:
        for model in models:
            statement = select(func.count()).select_from(model)
            row_count = session.scalar(statement)

            print(
                f"{model.__tablename__}: "
                f"{row_count} row(s)"
            )


def test_models() -> None:
    try:
        check_tables()
        check_model_queries()

        print("\nAll ORM models work correctly!")

    except SQLAlchemyError as error:
        print("\nDatabase or model error:")
        print(error)
        raise

    except Exception as error:
        print("\nError:")
        print(error)
        raise


if __name__ == "__main__":
    test_models()