from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.base import Base


if TYPE_CHECKING:
    from backend.models.quiz import Quiz
    from backend.models.user import User


class Document(Base):
    __tablename__ = "documents"

    __table_args__ = (
        CheckConstraint(
            "file_size_bytes >= 0",
        ),
        CheckConstraint(
            """
            processing_status IN (
                'uploaded',
                'processing',
                'ready',
                'failed'
            )
            """
        ),
    )

    document_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    subject: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    file_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'uploaded'"),
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    teacher: Mapped["User"] = relationship(
        back_populates="documents",
    )

    quizzes: Mapped[list["Quiz"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    preview_file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
