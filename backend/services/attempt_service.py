from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.models import (
    Question,
    Quiz,
    QuizAttempt,
    StudentAnswer,
    User,
)


VALID_ATTEMPT_STATUSES = {
    "in_progress",
    "submitted",
    "graded",
}


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _to_nonnegative_decimal(
    value: Decimal | int | float | str,
    field_name: str,
) -> Decimal:
    try:
        decimal_value = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} must be a valid number."
        ) from error

    if decimal_value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return decimal_value


# ==================================================
# GET ATTEMPT BY ID
# ==================================================

def get_attempt_by_id(
    session: Session,
    attempt_id: int,
) -> QuizAttempt | None:
    statement = (
        select(QuizAttempt)
        .options(
            selectinload(QuizAttempt.quiz),
            selectinload(QuizAttempt.student),
            selectinload(QuizAttempt.answers)
            .selectinload(StudentAnswer.question),
            selectinload(QuizAttempt.answers)
            .selectinload(StudentAnswer.selected_option),
        )
        .where(QuizAttempt.attempt_id == attempt_id)
    )

    return session.scalar(statement)


# ==================================================
# GET STUDENT ATTEMPTS
# ==================================================

def get_attempts_by_student(
    session: Session,
    student_id: int,
) -> list[QuizAttempt]:
    statement = (
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz))
        .where(QuizAttempt.student_id == student_id)
        .order_by(QuizAttempt.started_at.desc())
    )

    return list(session.scalars(statement).all())


# ==================================================
# GET QUIZ ATTEMPTS
# ==================================================

def get_attempts_by_quiz(
    session: Session,
    quiz_id: int,
) -> list[QuizAttempt]:
    statement = (
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.student))
        .where(QuizAttempt.quiz_id == quiz_id)
        .order_by(QuizAttempt.started_at.desc())
    )

    return list(session.scalars(statement).all())


# ==================================================
# GET ACTIVE ATTEMPT
# ==================================================

def get_active_attempt(
    session: Session,
    quiz_id: int,
    student_id: int,
) -> QuizAttempt | None:
    statement = select(QuizAttempt).where(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == student_id,
        QuizAttempt.status == "in_progress",
    )

    return session.scalar(statement)


# ==================================================
# GET NEXT ATTEMPT NUMBER
# ==================================================

def get_next_attempt_number(
    session: Session,
    quiz_id: int,
    student_id: int,
) -> int:
    statement = select(
        func.max(QuizAttempt.attempt_number)
    ).where(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == student_id,
    )

    latest_attempt_number = session.scalar(statement)

    if latest_attempt_number is None:
        return 1

    return latest_attempt_number + 1


# ==================================================
# CALCULATE MAXIMUM QUIZ SCORE
# ==================================================

def calculate_maximum_score(
    session: Session,
    quiz_id: int,
) -> Decimal:
    statement = select(
        func.sum(Question.points)
    ).where(
        Question.quiz_id == quiz_id
    )

    maximum_score = session.scalar(statement)

    if maximum_score is None:
        return Decimal("0.00")

    return Decimal(maximum_score)


# ==================================================
# START QUIZ ATTEMPT
# ==================================================

def start_quiz_attempt(
    session: Session,
    quiz_id: int,
    student_id: int,
) -> QuizAttempt:
    quiz = session.get(Quiz, quiz_id)

    if quiz is None:
        raise ValueError("Quiz not found.")

    if quiz.status != "published":
        raise ValueError(
            "Only published quizzes can be started."
        )

    student = session.get(User, student_id)

    if student is None:
        raise ValueError("Student not found.")

    if student.role != "student":
        raise ValueError(
            "Only users with the student role "
            "can start quiz attempts."
        )

    active_attempt = get_active_attempt(
        session=session,
        quiz_id=quiz_id,
        student_id=student_id,
    )

    if active_attempt is not None:
        raise ValueError(
            "The student already has an active "
            "attempt for this quiz."
        )

    maximum_score = calculate_maximum_score(
        session=session,
        quiz_id=quiz_id,
    )

    if maximum_score <= 0:
        raise ValueError(
            "The quiz must contain at least one "
            "question before it can be started."
        )

    attempt_number = get_next_attempt_number(
        session=session,
        quiz_id=quiz_id,
        student_id=student_id,
    )

    new_attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        attempt_number=attempt_number,
        status="in_progress",
        maximum_score=maximum_score,
    )

    try:
        session.add(new_attempt)
        session.commit()
        session.refresh(new_attempt)

        created_attempt = get_attempt_by_id(
            session=session,
            attempt_id=new_attempt.attempt_id,
        )

        if created_attempt is None:
            raise RuntimeError(
                "Attempt was created but could "
                "not be reloaded."
            )

        return created_attempt

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# SUBMIT QUIZ ATTEMPT
# ==================================================

def submit_quiz_attempt(
    session: Session,
    attempt_id: int,
) -> QuizAttempt | None:
    attempt = session.get(QuizAttempt, attempt_id)

    if attempt is None:
        return None

    if attempt.status != "in_progress":
        raise ValueError(
            "Only an in-progress attempt "
            "can be submitted."
        )

    try:
        attempt.status = "submitted"
        attempt.submitted_at = datetime.now(
            timezone.utc
        )

        session.commit()
        session.refresh(attempt)

        return attempt

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# GRADE QUIZ ATTEMPT
# ==================================================

def grade_quiz_attempt(
    session: Session,
    attempt_id: int,
    score: Decimal | int | float | str,
) -> QuizAttempt | None:
    attempt = session.get(QuizAttempt, attempt_id)

    if attempt is None:
        return None

    if attempt.status != "submitted":
        raise ValueError(
            "The attempt must be submitted "
            "before it can be graded."
        )

    cleaned_score = _to_nonnegative_decimal(
        score,
        "Score",
    )

    if attempt.maximum_score is None:
        attempt.maximum_score = calculate_maximum_score(
            session=session,
            quiz_id=attempt.quiz_id,
        )

    if cleaned_score > attempt.maximum_score:
        raise ValueError(
            "The score cannot be greater than "
            "the maximum score."
        )

    try:
        attempt.score = cleaned_score
        attempt.status = "graded"

        session.commit()
        session.refresh(attempt)

        return attempt

    except SQLAlchemyError:
        session.rollback()
        raise