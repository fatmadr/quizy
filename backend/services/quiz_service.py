from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.models import (
    Document,
    Question,
    QuestionOption,
    Quiz,
)


VALID_QUIZ_STATUSES = {
    "draft",
    "published",
    "archived",
}

VALID_DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
}

VALID_QUESTION_TYPES = {
    "mcq",
    "open",
}


# ==================================================
# INTERNAL VALIDATION HELPERS
# ==================================================

def _clean_required_text(
    value: Any,
    field_name: str,
    maximum_length: int | None = None,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")

    cleaned_value = value.strip()

    if not cleaned_value:
        raise ValueError(f"{field_name} is required.")

    if (
        maximum_length is not None
        and len(cleaned_value) > maximum_length
    ):
        raise ValueError(
            f"{field_name} cannot exceed "
            f"{maximum_length} characters."
        )

    return cleaned_value


def _clean_optional_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("Optional text values must be strings.")

    cleaned_value = value.strip()

    return cleaned_value or None


def _to_positive_decimal(
    value: Any,
    field_name: str,
) -> Decimal:
    try:
        decimal_value = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} must be a valid number."
        ) from error

    if decimal_value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return decimal_value


def _to_positive_position(
    value: Any,
    field_name: str,
) -> int:
    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a positive integer."
        )

    try:
        position = int(value)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} must be a positive integer."
        ) from error

    if position <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return position


# ==================================================
# GET QUIZ BY ID
# ==================================================

def get_quiz_by_id(
    session: Session,
    quiz_id: int,
) -> Quiz | None:
    statement = (
        select(Quiz)
        .options(
            selectinload(Quiz.document),
            selectinload(Quiz.questions)
            .selectinload(Question.options),
        )
        .where(Quiz.quiz_id == quiz_id)
    )

    return session.scalar(statement)


# ==================================================
# GET QUIZZES BY DOCUMENT
# ==================================================

def get_quiz_by_document(
    session: Session,
    document_id: int,
) -> list[Quiz]:
    statement = (
        select(Quiz)
        .where(Quiz.document_id == document_id)
        .order_by(Quiz.created_at.desc())
    )

    return list(session.scalars(statement).all())


# ==================================================
# GET ALL QUIZZES
# ==================================================

def get_all_quiz(
    session: Session,
) -> list[Quiz]:
    statement = (
        select(Quiz)
        .options(selectinload(Quiz.document))
        .order_by(Quiz.created_at.desc())
    )

    return list(session.scalars(statement).all())


# ==================================================
# BUILD QUESTION OPTION
# ==================================================

def _build_option(
    option_data: dict[str, Any],
) -> QuestionOption:
    option_text = _clean_required_text(
        option_data.get("option_text"),
        "Option text",
    )

    position = _to_positive_position(
        option_data.get("position"),
        "Option position",
    )

    is_correct = option_data.get("is_correct", False)

    if not isinstance(is_correct, bool):
        raise ValueError(
            "Option is_correct must be True or False."
        )

    return QuestionOption(
        option_text=option_text,
        is_correct=is_correct,
        position=position,
    )


# ==================================================
# BUILD QUESTION
# ==================================================

def _build_question(
    question_data: dict[str, Any],
) -> Question:
    question_text = _clean_required_text(
        question_data.get("question_text"),
        "Question text",
    )

    question_type_value = question_data.get(
        "question_type"
    )

    if not isinstance(question_type_value, str):
        raise ValueError(
            "Question type must be 'mcq' or 'open'."
        )

    question_type = question_type_value.strip().lower()

    if question_type not in VALID_QUESTION_TYPES:
        raise ValueError(
            "Question type must be 'mcq' or 'open'."
        )

    points = _to_positive_decimal(
        question_data.get("points", 1),
        "Question points",
    )

    position = _to_positive_position(
        question_data.get("position"),
        "Question position",
    )

    explanation = _clean_optional_text(
        question_data.get("explanation")
    )

    options_data = question_data.get("options", [])

    if not isinstance(options_data, list):
        raise ValueError(
            "Question options must be provided as a list."
        )

    question = Question(
        question_text=question_text,
        question_type=question_type,
        points=points,
        position=position,
        explanation=explanation,
    )

    if question_type == "open":
        if options_data:
            raise ValueError(
                "Open questions cannot have options."
            )

        return question

    if len(options_data) < 2:
        raise ValueError(
            "An MCQ must contain at least two options."
        )

    option_positions: set[int] = set()
    correct_option_count = 0

    for option_data in options_data:
        if not isinstance(option_data, dict):
            raise ValueError(
                "Every option must be a dictionary."
            )

        option = _build_option(option_data)

        if option.position in option_positions:
            raise ValueError(
                f"Duplicate option position "
                f"{option.position}."
            )

        option_positions.add(option.position)

        if option.is_correct:
            correct_option_count += 1

        question.options.append(option)

    if correct_option_count != 1:
        raise ValueError(
            "An MCQ must have exactly one correct option."
        )

    return question


# ==================================================
# CREATE COMPLETE QUIZ
# ==================================================

def create_quiz(
    session: Session,
    document_id: int,
    title: str,
    questions_data: list[dict[str, Any]],
    description: str | None = None,
    difficulty: str = "medium",
    time_limit_minutes: int | None = None,
    status: str = "draft",
) -> Quiz:
    document = session.get(Document, document_id)

    if document is None:
        raise ValueError("Document not found.")

    cleaned_title = _clean_required_text(
        title,
        "Quiz title",
        maximum_length=200,
    )

    cleaned_description = _clean_optional_text(
        description
    )

    normalized_status = status.strip().lower()
    normalized_difficulty = difficulty.strip().lower()

    if normalized_status not in VALID_QUIZ_STATUSES:
        raise ValueError(
            "Quiz status must be 'draft', "
            "'published', or 'archived'."
        )

    if normalized_difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            "Quiz difficulty must be 'easy', "
            "'medium', or 'hard'."
        )

    if time_limit_minutes is not None:
        if (
            isinstance(time_limit_minutes, bool)
            or not isinstance(time_limit_minutes, int)
            or time_limit_minutes <= 0
        ):
            raise ValueError(
                "Time limit must be a positive integer."
            )

    if not isinstance(questions_data, list):
        raise ValueError(
            "Questions must be provided as a list."
        )

    if not questions_data:
        raise ValueError(
            "A quiz must contain at least one question."
        )

    new_quiz = Quiz(
        document_id=document_id,
        title=cleaned_title,
        description=cleaned_description,
        status=normalized_status,
        difficulty=normalized_difficulty,
        time_limit_minutes=time_limit_minutes,
    )

    question_positions: set[int] = set()

    for question_data in questions_data:
        if not isinstance(question_data, dict):
            raise ValueError(
                "Every question must be a dictionary."
            )

        question = _build_question(question_data)

        if question.position in question_positions:
            raise ValueError(
                f"Duplicate question position "
                f"{question.position}."
            )

        question_positions.add(question.position)
        new_quiz.questions.append(question)

    if normalized_status == "published":
        new_quiz.published_at = datetime.now(
            timezone.utc
        )

    try:
        session.add(new_quiz)
        session.commit()
        session.refresh(new_quiz)

        created_quiz = get_quiz_by_id(
            session=session,
            quiz_id=new_quiz.quiz_id,
        )

        if created_quiz is None:
            raise RuntimeError(
                "Quiz was created but could not be reloaded."
            )

        return created_quiz

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# UPDATE QUIZ STATUS
# ==================================================

def update_quiz_status(
    session: Session,
    quiz_id: int,
    new_status: str,
) -> Quiz | None:
    quiz = session.get(Quiz, quiz_id)

    if quiz is None:
        return None

    normalized_status = new_status.strip().lower()

    if normalized_status not in VALID_QUIZ_STATUSES:
        raise ValueError(
            "Quiz status must be 'draft', "
            "'published', or 'archived'."
        )

    try:
        quiz.status = normalized_status

        if normalized_status == "published":
            if quiz.published_at is None:
                quiz.published_at = datetime.now(
                    timezone.utc
                )

        elif normalized_status == "draft":
            quiz.published_at = None

        session.commit()
        session.refresh(quiz)

        return quiz

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# DELETE QUIZ
# ==================================================

def delete_quiz(
    session: Session,
    quiz_id: int,
) -> bool:
    quiz = session.get(Quiz, quiz_id)

    if quiz is None:
        return False

    try:
        session.delete(quiz)
        session.commit()

        return True

    except SQLAlchemyError:
        session.rollback()
        raise