from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Question(Base):
    __tablename__ = "questions"

    __table_args__ = (
        CheckConstraint(
            "question_type IN ('mcq', 'open')",
            name="check_question_type",
        ),
        CheckConstraint(
            "points > 0",
            name="check_question_points",
        ),
        CheckConstraint(
            "position > 0",
            name="check_question_position",
        ),
        UniqueConstraint(
            "quiz_id",
            "position",
            name="uq_question_position",
        ),
    )

    question_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    quiz_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "quizzes.quiz_id",
            name="fk_questions_quiz",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    points: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        server_default=text("1"),
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )