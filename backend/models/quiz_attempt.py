from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.quiz import Quiz
    from backend.models.user import User
    from backend.models.student_answer import StudentAnswer

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    __table_args__ = (
        CheckConstraint(
            "attempt_number > 0",
            name="check_attempt_number_positive",
        ),
        CheckConstraint(
            "status IN ('in_progress', 'submitted', 'graded')",
            name="check_attempt_status",
        ),
        CheckConstraint(
            "score IS NULL OR score >= 0",
            name="check_attempt_score",
        ),
        CheckConstraint(
            "maximum_score IS NULL OR maximum_score >= 0",
            name="check_attempt_maximum_score",
        ),
        UniqueConstraint(
            "quiz_id",
            "student_id",
            "attempt_number",
            name="uq_student_quiz_attempt",
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    quiz_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "quizzes.quiz_id",
            name="fk_attempts_quiz",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            name="fk_attempts_student",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'in_progress'"),
    )

    score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    maximum_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    quiz: Mapped["Quiz"] = relationship(
        back_populates="attempts",
    )

    student: Mapped["User"] = relationship(
        back_populates="quiz_attempts",
    )

    answers: Mapped[list["StudentAnswer"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )