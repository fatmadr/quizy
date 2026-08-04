from pathlib import Path

import pythoncom
import win32com.client


SUPPORTED_PREVIEW_TYPES = {
    ".pdf",
    ".docx",
    ".pptx",
}


# ==================================================
# DOCX -> PDF
# ==================================================

def create_docx_preview(
    source_path: Path,
    preview_path: Path,
) -> None:
    word = None
    document = None

    pythoncom.CoInitialize()

    try:
        word = win32com.client.DispatchEx(
            "Word.Application"
        )

        word.Visible = False
        word.DisplayAlerts = 0

        document = word.Documents.Open(
            str(source_path.resolve()),
            ReadOnly=True,
        )

        # 17 = PDF
        document.ExportAsFixedFormat(
            OutputFileName=str(
                preview_path.resolve()
            ),
            ExportFormat=17,
        )

    finally:
        if document is not None:
            document.Close(False)

        if word is not None:
            word.Quit()

        pythoncom.CoUninitialize()


# ==================================================
# PPTX -> PDF
# ==================================================

def create_pptx_preview(
    source_path: Path,
    preview_path: Path,
) -> None:
    powerpoint = None
    presentation = None

    pythoncom.CoInitialize()

    try:
        powerpoint = (
            win32com.client.DispatchEx(
                "PowerPoint.Application"
            )
        )

        presentation = (
            powerpoint.Presentations.Open(
                str(source_path.resolve()),
                WithWindow=False,
            )
        )

        # 32 = PDF
        presentation.SaveAs(
            str(preview_path.resolve()),
            32,
        )

    finally:
        if presentation is not None:
            presentation.Close()

        if powerpoint is not None:
            powerpoint.Quit()

        pythoncom.CoUninitialize()


# ==================================================
# CREATE DOCUMENT PREVIEW
# ==================================================

def create_document_preview(
    source_path: Path,
    preview_directory: Path,
) -> Path:

    extension = source_path.suffix.lower()

    if extension not in SUPPORTED_PREVIEW_TYPES:
        raise ValueError(
            "Preview is supported only for "
            "PDF, DOCX, and PPTX files."
        )

    # PDF needs no conversion
    if extension == ".pdf":
        return source_path

    preview_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    preview_path = (
        preview_directory
        / f"{source_path.stem}.pdf"
    )

    try:
        if extension == ".docx":
            create_docx_preview(
                source_path,
                preview_path,
            )

        elif extension == ".pptx":
            create_pptx_preview(
                source_path,
                preview_path,
            )

    except Exception as error:
        print(
            "Document conversion error:",
            repr(error),
        )

        raise RuntimeError(
            "The document could not be converted "
            "to a PDF preview."
        ) from error

    if not preview_path.is_file():
        raise RuntimeError(
            "The PDF preview was not created."
        )

    return preview_path