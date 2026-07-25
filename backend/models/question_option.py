from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    Text,
    UniqueConstraint,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class QuestionOption(Base):
    __tablename__ = "question_options"

    __table_args__ = (
        CheckConstraint(
            "position > 0",
            name="check_option_position",
        ),
        UniqueConstraint(
            "question_id",
            "position",
            name="uq_option_position",
        ),
    )

    option_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    question_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "questions.question_id",
            name="fk_options_question",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    option_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )