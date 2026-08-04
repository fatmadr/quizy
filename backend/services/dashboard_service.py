from datetime import datetime, timedelta, timezone

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from backend.models import (
    Document,
    Quiz,
    QuizAttempt,
)


# ==================================================
# TOTAL DOCUMENTS
# ==================================================

def count_teacher_documents(
    session: Session,
    teacher_id: int,
) -> int:
    statement = (
        select(func.count(Document.document_id))
        .where(Document.teacher_id == teacher_id)
    )

    return session.scalar(statement) or 0


# ==================================================
# TOTAL QUIZZES
# ==================================================

def count_teacher_quizzes(
    session: Session,
    teacher_id: int,
) -> int:
    statement = (
        select(func.count(Quiz.quiz_id))
        .join(
            Document,
            Quiz.document_id == Document.document_id,
        )
        .where(Document.teacher_id == teacher_id)
    )

    return session.scalar(statement) or 0


# ==================================================
# ACTIVE STUDENTS
# ==================================================

def count_teacher_students(
    session: Session,
    teacher_id: int,
) -> int:
    statement = (
        select(
            func.count(
                distinct(QuizAttempt.student_id)
            )
        )
        .join(
            Quiz,
            QuizAttempt.quiz_id == Quiz.quiz_id,
        )
        .join(
            Document,
            Quiz.document_id == Document.document_id,
        )
        .where(Document.teacher_id == teacher_id)
    )

    return session.scalar(statement) or 0


# ==================================================
# RECENT QUIZZES
# ==================================================

def count_recent_teacher_quizzes(
    session: Session,
    teacher_id: int,
) -> int:
    seven_days_ago = (
        datetime.now(timezone.utc)
        - timedelta(days=7)
    )

    statement = (
        select(func.count(Quiz.quiz_id))
        .join(
            Document,
            Quiz.document_id == Document.document_id,
        )
        .where(
            Document.teacher_id == teacher_id,
            Quiz.created_at >= seven_days_ago,
        )
    )

    return session.scalar(statement) or 0


# ==================================================
# DASHBOARD STATISTICS
# ==================================================

def get_teacher_dashboard_stats(
    session: Session,
    teacher_id: int,
) -> dict[str, int]:
    return {
        "documents": count_teacher_documents(
            session,
            teacher_id,
        ),
        "quizzes": count_teacher_quizzes(
            session,
            teacher_id,
        ),
        "students": count_teacher_students(
            session,
            teacher_id,
        ),
        "recent_quizzes": count_recent_teacher_quizzes(
            session,
            teacher_id,
        ),
    }