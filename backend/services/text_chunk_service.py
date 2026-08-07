import re


# ==================================================
# CLEAN TEXT
# ==================================================

def clean_text_for_chunking(
    text: str,
) -> str:

    if not text:
        return ""

    cleaned_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Keep paragraph breaks
        if not line:
            cleaned_lines.append("")
            continue

        # Remove long answer lines such as:
        # ....................
        # ……………………………………
        if (
            len(line) >= 8
            and all(
                character in ".…_- "
                for character in line
            )
        ):
            continue

        # Normalize spaces
        line = re.sub(
            r"[ \t]+",
            " ",
            line,
        )

        cleaned_lines.append(line)

    cleaned_text = "\n".join(
        cleaned_lines
    )

    # Avoid too many empty lines
    cleaned_text = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned_text,
    )

    return cleaned_text.strip()


# ==================================================
# SPLIT LARGE PARAGRAPH
# ==================================================

def split_large_paragraph(
    paragraph: str,
    max_size: int,
) -> list[str]:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        paragraph,
    )

    pieces = []
    current_piece = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Normal sentence fits
        if len(sentence) <= max_size:

            candidate = (
                f"{current_piece} {sentence}".strip()
            )

            if len(candidate) <= max_size:
                current_piece = candidate

            else:
                if current_piece:
                    pieces.append(
                        current_piece
                    )

                current_piece = sentence

        # Extremely long sentence
        else:
            if current_piece:
                pieces.append(
                    current_piece
                )

                current_piece = ""

            words = sentence.split()

            word_piece = ""

            for word in words:

                candidate = (
                    f"{word_piece} {word}".strip()
                )

                if len(candidate) <= max_size:
                    word_piece = candidate

                else:
                    if word_piece:
                        pieces.append(
                            word_piece
                        )

                    word_piece = word

            if word_piece:
                pieces.append(
                    word_piece
                )

    if current_piece:
        pieces.append(
            current_piece
        )

    return pieces


# ==================================================
# SPLIT TEXT INTO CHUNKS
# ==================================================

def split_text_into_chunks(
    text: str,
    chunk_size: int = 1800,
    overlap_paragraphs: int = 1,
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    if overlap_paragraphs < 0:
        raise ValueError(
            "Overlap paragraphs cannot be negative."
        )

    cleaned_text = clean_text_for_chunking(
        text
    )

    if not cleaned_text:
        return []

    # ----------------------------------------------
    # CREATE PARAGRAPHS
    # ----------------------------------------------

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            cleaned_text,
        )
        if paragraph.strip()
    ]

    # ----------------------------------------------
    # HANDLE VERY LARGE PARAGRAPHS
    # ----------------------------------------------

    units = []

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:
            units.append(
                paragraph
            )

        else:
            units.extend(
                split_large_paragraph(
                    paragraph=paragraph,
                    max_size=chunk_size,
                )
            )

    # ----------------------------------------------
    # BUILD CHUNKS
    # ----------------------------------------------

    chunks = []

    current_units = []

    for unit in units:

        candidate_units = (
            current_units
            + [unit]
        )

        candidate_text = "\n\n".join(
            candidate_units
        )

        # Unit still fits in current chunk
        if (
            not current_units
            or len(candidate_text)
            <= chunk_size
        ):
            current_units.append(
                unit
            )

            continue

        # Save completed chunk
        completed_chunk = "\n\n".join(
            current_units
        ).strip()

        if completed_chunk:
            chunks.append(
                completed_chunk
            )

        # ------------------------------------------
        # PARAGRAPH-LEVEL OVERLAP
        # ------------------------------------------

        if overlap_paragraphs > 0:
            current_units = current_units[
                -overlap_paragraphs:
            ]

        else:
            current_units = []

        # Don't keep overlap if it makes
        # the next chunk too large.
        while current_units:

            test_text = "\n\n".join(
                current_units
                + [unit]
            )

            if len(test_text) <= chunk_size:
                break

            current_units.pop(0)

        current_units.append(
            unit
        )

    # ----------------------------------------------
    # FINAL CHUNK
    # ----------------------------------------------

    if current_units:

        final_chunk = "\n\n".join(
            current_units
        ).strip()

        if final_chunk:
            chunks.append(
                final_chunk
            )

    return chunks