from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import Document, User


VALID_PROCESSING_STATUSES = {
    "uploaded",
    "processing",
    "ready",
    "failed",
}

# ==================================================
# GET DOCUMENT BY ID
# ==================================================

def get_document_by_id(
    session: Session,
    document_id: int,
) -> Document | None:
    return session.get(Document, document_id)

# ==================================================
# GET DOCUMENT BY FILE PATH
# ==================================================

def get_document_by_file_path(
    session: Session,
    file_path: str,
) -> Document | None:
    normalized_path = file_path.strip()

    statement = select(Document).where(
        Document.file_path == normalized_path
    )

    return session.scalar(statement)


# ==================================================
# GET DOCUMENTS UPLOADED BY A TEACHER
# ==================================================

def get_documents_by_teacher(
    session: Session,
    teacher_id: int,
) -> list[Document]:
    statement = (
        select(Document)
        .where(Document.teacher_id == teacher_id)
        .order_by(Document.uploaded_at.desc())
    )

    return list(session.scalars(statement).all())


# ==================================================
# GET ALL DOCUMENTS
# ==================================================

def get_all_documents(
    session: Session,
) -> list[Document]:
    statement = select(Document).order_by(
        Document.uploaded_at.desc()
    )

    return list(session.scalars(statement).all())


# ==================================================
# CREATE DOCUMENT
# ==================================================

def create_document(
    session: Session,
    teacher_id: int,
    title: str,
    original_filename: str,
    file_path: str,
    subject: str,
    preview_file_path: str | None = None,
    file_type: str | None = None,
    file_size_bytes: int | None = None,
) -> Document:

    cleaned_title = title.strip()
    cleaned_filename = original_filename.strip()
    cleaned_file_path = file_path.strip()
    cleaned_subject = subject.strip()
    cleaned_preview_file_path = (
        preview_file_path.strip()
        if preview_file_path is not None
        else None
    )

    if not cleaned_title:
        raise ValueError("Document title is required.")

    if len(cleaned_title) > 200:
        raise ValueError(
            "Document title cannot exceed 200 characters."
        )

    if not cleaned_filename:
        raise ValueError(
            "The original filename is required."
        )

    if len(cleaned_filename) > 255:
        raise ValueError(
            "The filename cannot exceed 255 characters."
        )

    if not cleaned_file_path:
        raise ValueError("The file path is required.")

    if not cleaned_subject:
        raise ValueError("Document subject is required.")

    if len(cleaned_subject) > 100:
        raise ValueError(
            "Document subject cannot exceed 100 characters."
        )

    if file_size_bytes is not None and file_size_bytes < 0:
        raise ValueError(
            "The file size cannot be negative."
        )

    teacher = session.get(User, teacher_id)

    if teacher is None:
        raise ValueError("Teacher not found.")

    if teacher.role != "teacher":
        raise ValueError(
            "Only a teacher can upload a document."
        )

    existing_document = get_document_by_file_path(
        session=session,
        file_path=cleaned_file_path,
    )

    if existing_document is not None:
        raise ValueError(
            "A document with this file path already exists."
        )

    new_document = Document(
        teacher_id=teacher_id,
        title=cleaned_title,
        original_filename=cleaned_filename,
        file_path=cleaned_file_path,
        preview_file_path=cleaned_preview_file_path,
        subject=cleaned_subject,
        file_type=(
            file_type.strip()
            if file_type is not None
            else None
        ),
        file_size_bytes=file_size_bytes,
    )

    try:
        session.add(new_document)
        session.commit()
        session.refresh(new_document)

        return new_document

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# UPDATE DOCUMENT TITLE
# ==================================================

def update_document_title(
    session: Session,
    document_id: int,
    new_title: str,
) -> Document | None:
    document = session.get(Document, document_id)

    if document is None:
        return None

    cleaned_title = new_title.strip()

    if not cleaned_title:
        raise ValueError("Document title is required.")

    if len(cleaned_title) > 200:
        raise ValueError(
            "Document title cannot exceed 200 characters."
        )

    try:
        document.title = cleaned_title

        session.commit()
        session.refresh(document)

        return document

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# UPDATE PROCESSING STATUS
# ==================================================

def update_document_status(
    session: Session,
    document_id: int,
    new_status: str,
) -> Document | None:
    document = session.get(Document, document_id)

    if document is None:
        return None

    normalized_status = new_status.strip().lower()

    if normalized_status not in VALID_PROCESSING_STATUSES:
        raise ValueError(
            "Status must be 'uploaded', 'processing', "
            "'ready', or 'failed'."
        )

    try:
        document.processing_status = normalized_status

        session.commit()
        session.refresh(document)

        return document

    except SQLAlchemyError:
        session.rollback()
        raise


# ==================================================
# DELETE DOCUMENT
# ==================================================

def delete_document(
    session: Session,
    document_id: int,
    teacher_id: int,
) -> bool:
    document = session.get(
        Document,
        document_id,
    )

    if document is None:
        return False

    if document.teacher_id != teacher_id:
        raise ValueError(
            "You do not have permission "
            "to delete this document."
        )

    try:
        session.delete(document)
        session.commit()

        return True

    except SQLAlchemyError:
        session.rollback()
        raise