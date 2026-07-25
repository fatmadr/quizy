from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class StudentAnswer(Base):
    __tablename__ = "student_answers"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_attempt_question",
        ),
        CheckConstraint(
            """
            selected_option_id IS NOT NULL
            OR answer_text IS NOT NULL
            """,
            name="chk_answer_provided",
        ),
    )

    answer_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "quiz_attempts.attempt_id",
            name="fk_answers_attempt",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    question_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "questions.question_id",
            name="fk_answers_question",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    selected_option_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "question_options.option_id",
            name="fk_answers_selected_option",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    answer_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_correct: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    points_awarded: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        server_default=text("0"),
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )