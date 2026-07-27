from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.models import (
    Question,
    QuestionOption,
    QuizAttempt,
    StudentAnswer,
)
from backend.services.attempt_service import (
    calculate_maximum_score,
)


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


def _get_attempt_and_question(
    session: Session,
    attempt_id: int,
    question_id: int,
) -> tuple[QuizAttempt, Question]:
    attempt = session.get(QuizAttempt, attempt_id)

    if attempt is None:
        raise ValueError("Quiz attempt not found.")

    question = session.get(Question, question_id)

    if question is None:
        raise ValueError("Question not found.")

    if question.quiz_id != attempt.quiz_id:
        raise ValueError(
            "This question does not belong to "
            "the attempted quiz."
        )

    return attempt, question


# ==================================================
# GET ANSWER BY ID
# ==================================================

def get_answer_by_id(
    session: Session,
    answer_id: int,
) -> StudentAnswer | None:
    statement = (
        select(StudentAnswer)
        .options(
            selectinload(StudentAnswer.attempt),
            selectinload(StudentAnswer.question),
            selectinload(StudentAnswer.selected_option),
        )
        .where(StudentAnswer.answer_id == answer_id)
    )

    return session.scalar(statement)


# ==================================================
# GET ANSWER FOR ONE QUESTION
# ==================================================

def get_answer_for_question(
    session: Session,
    attempt_id: int,
    question_id: int,
) -> StudentAnswer | None:
    statement = select(StudentAnswer).where(
        StudentAnswer.attempt_id == attempt_id,
        StudentAnswer.question_id == question_id,
    )

    return session.scalar(statement)


# ==================================================
# GET ALL ANSWERS FOR AN ATTEMPT
# ==================================================

def get_answers_by_attempt(
    session: Session,
    attempt_id: int,
) -> list[StudentAnswer]:
    statement = (
        select(StudentAnswer)
        .join(StudentAnswer.question)
        .options(
            selectinload(StudentAnswer.question),
            selectinload(StudentAnswer.selected_option),
        )
        .where(StudentAnswer.attempt_id == attempt_id)
        .order_by(Question.position)
    )

    return list(session.scalars(statement).all())


# ==================================================
# SAVE MCQ ANSWER
# ==================================================

def save_mcq_answer(
    session: Session,
    attempt_id: int,
    question_id: int,
    selected_option_id: int,
) -> StudentAnswer:
    attempt, question = _get_attempt_and_question(
        session=session,
        attempt_id=attempt_id,
        question_id=question_id,
    )

    if attempt.status != "in_progress":
        raise ValueError(
            "Answers can only be changed while "
            "the attempt is in progress."
        )

    if question.question_type != "mcq":
        raise ValueError(
            "This question is not an MCQ."
        )

    selected_option = session.get(
        QuestionOption,
        selected_option_id,
    )

    if selected_option is None:
        raise ValueError(
            "The selected option was not found."
        )

    if selected_option.question_id != question_id:
        raise ValueError(
            "The selected option does not belong "
            "to this question."
        )

    answer = get_answer_for_question(
        session=session,
        attempt_id=attempt_id,
        question_id=question_id,
    )

    if answer is None:
        answer = StudentAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
        )

        session.add(answer)

    answer.selected_option_id = selected_option_id
    answer.answer_text = None
    answer.is_correct = selected_option.is_correct

    if selected_option.is_correct:
        answer.points_awarded = question.points
    else:
        answer.points_awarded = Decimal("0.00")

    answer.feedback = question.explanation

    try:
        session.commit()
        session.refresh(answer)

        return answer

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# SAVE OPEN ANSWER
# ==================================================

def save_open_answer(
    session: Session,
    attempt_id: int,
    question_id: int,
    answer_text: str,
) -> StudentAnswer:
    attempt, question = _get_attempt_and_question(
        session=session,
        attempt_id=attempt_id,
        question_id=question_id,
    )

    if attempt.status != "in_progress":
        raise ValueError(
            "Answers can only be changed while "
            "the attempt is in progress."
        )

    if question.question_type != "open":
        raise ValueError(
            "This question is not an open question."
        )

    cleaned_answer = answer_text.strip()

    if not cleaned_answer:
        raise ValueError(
            "A written answer is required."
        )

    answer = get_answer_for_question(
        session=session,
        attempt_id=attempt_id,
        question_id=question_id,
    )

    if answer is None:
        answer = StudentAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
        )

        session.add(answer)

    answer.selected_option_id = None
    answer.answer_text = cleaned_answer

    # The open answer has not been evaluated yet.
    answer.is_correct = None
    answer.points_awarded = Decimal("0.00")
    answer.feedback = None

    try:
        session.commit()
        session.refresh(answer)

        return answer

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# GRADE OPEN ANSWER
# ==================================================

def grade_open_answer(
    session: Session,
    answer_id: int,
    points_awarded: Decimal | int | float | str,
    feedback: str | None = None,
) -> StudentAnswer:
    answer = session.get(StudentAnswer, answer_id)

    if answer is None:
        raise ValueError("Student answer not found.")

    question = session.get(
        Question,
        answer.question_id,
    )

    if question is None:
        raise ValueError("Question not found.")

    if question.question_type != "open":
        raise ValueError(
            "Only open answers require manual "
            "or AI grading."
        )

    attempt = session.get(
        QuizAttempt,
        answer.attempt_id,
    )

    if attempt is None:
        raise ValueError("Quiz attempt not found.")

    if attempt.status not in {"submitted", "graded"}:
        raise ValueError(
            "The attempt must be submitted "
            "before its open answers are graded."
        )

    cleaned_points = _to_nonnegative_decimal(
        points_awarded,
        "Points awarded",
    )

    if cleaned_points > question.points:
        raise ValueError(
            "Awarded points cannot exceed "
            "the question's maximum points."
        )

    cleaned_feedback = None

    if feedback is not None:
        cleaned_feedback = feedback.strip() or None

    answer.points_awarded = cleaned_points
    answer.feedback = cleaned_feedback

    # Full points means fully correct.
    # Zero or partial points means not fully correct.
    answer.is_correct = (
        cleaned_points == question.points
    )

    try:
        session.commit()
        session.refresh(answer)

        return answer

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# CALCULATE CURRENT ATTEMPT SCORE
# ==================================================

def calculate_attempt_score(
    session: Session,
    attempt_id: int,
) -> Decimal:
    statement = select(
        func.sum(StudentAnswer.points_awarded)
    ).where(
        StudentAnswer.attempt_id == attempt_id
    )

    total_score = session.scalar(statement)

    if total_score is None:
        return Decimal("0.00")

    return Decimal(total_score)


# ==================================================
# FINALIZE ATTEMPT GRADING
# ==================================================

def finalize_attempt_grading(
    session: Session,
    attempt_id: int,
) -> QuizAttempt:
    attempt = session.get(QuizAttempt, attempt_id)

    if attempt is None:
        raise ValueError("Quiz attempt not found.")

    if attempt.status != "submitted":
        raise ValueError(
            "Only a submitted attempt can be graded."
        )

    ungraded_open_answers_statement = (
        select(func.count())
        .select_from(StudentAnswer)
        .join(StudentAnswer.question)
        .where(
            StudentAnswer.attempt_id == attempt_id,
            Question.question_type == "open",
            StudentAnswer.is_correct.is_(None),
        )
    )

    ungraded_open_answers = session.scalar(
        ungraded_open_answers_statement
    )

    if ungraded_open_answers:
        raise ValueError(
            "All submitted open answers must be "
            "graded before finalizing the attempt."
        )

    total_score = calculate_attempt_score(
        session=session,
        attempt_id=attempt_id,
    )

    maximum_score = calculate_maximum_score(
        session=session,
        quiz_id=attempt.quiz_id,
    )

    if total_score > maximum_score:
        raise ValueError(
            "The calculated score cannot exceed "
            "the maximum quiz score."
        )

    try:
        attempt.score = total_score
        attempt.maximum_score = maximum_score
        attempt.status = "graded"

        session.commit()
        session.refresh(attempt)

        return attempt

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# DELETE ANSWER
# ==================================================

def delete_answer(
    session: Session,
    answer_id: int,
) -> bool:
    answer = session.get(StudentAnswer, answer_id)

    if answer is None:
        return False

    attempt = session.get(
        QuizAttempt,
        answer.attempt_id,
    )

    if attempt is None:
        raise ValueError("Quiz attempt not found.")

    if attempt.status != "in_progress":
        raise ValueError(
            "An answer cannot be deleted after "
            "the attempt is submitted."
        )

    try:
        session.delete(answer)
        session.commit()

        return True

    except SQLAlchemyError:
        session.rollback()
        raise