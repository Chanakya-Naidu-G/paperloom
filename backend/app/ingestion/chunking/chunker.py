import uuid
import re
from app.models.chunk import Chunk
from app.models.section import DocumentSection

MIN_CHUNK_LENGTH = 30
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SEPARATORS = (
    "\n\n",
    "\n",
    ". ",
    "? ",
    "! ",
    "; ",
    ", ",
    " ",
)

def _recursive_split(
    text: str,
    separators: tuple[str, ...] = SEPARATORS,
) -> list[str]:

    text = text.strip()

    if not text:
        return []

    if len(text) <= CHUNK_SIZE:
        return [text]

    if not separators:
        return [
            text[i:i + CHUNK_SIZE]
            for i in range(0, len(text), CHUNK_SIZE)
        ]

    separator = separators[0]

    if separator not in text:
        return _recursive_split(
            text,
            separators[1:]
        )

    parts = text.split(separator)

    chunks = []
    current = ""

    for part in parts:

        candidate = (
            part
            if not current
            else current + separator + part
        )

        if len(candidate) <= CHUNK_SIZE:
            current = candidate

        else:

            if current:
                chunks.extend(
                    _recursive_split(
                        current,
                        separators[1:]
                    )
                )

            current = part

    if current:
        chunks.extend(
            _recursive_split(
                current,
                separators[1:]
            )
        )

    return chunks


def _extract_overlap(
    text: str,
    max_chars: int,
) -> str:
    """
    Extracts an overlap region from the end of a chunk,
    preferring sentence boundaries.
    """

    if len(text) <= max_chars:
        return text

    sentences = re.split(r'(?<=[.!?])\s+', text)

    overlap = []

    current_size = 0

    for sentence in reversed(sentences):

        if current_size + len(sentence) > max_chars:

            break

        overlap.insert(0, sentence)

        current_size += len(sentence)

    if overlap:
        return " ".join(overlap)

    # Fallback if there are no sentence boundaries
    return text[-max_chars:]

def _apply_overlap(
    chunks: list[str],
) -> list[str]:

    if len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]

    for chunk in chunks[1:]:

        overlap = _extract_overlap(
            overlapped[-1],
            CHUNK_OVERLAP,
        )

        overlapped.append(
            overlap + "\n\n" + chunk
        )

    return overlapped
def _build_chunk(
    *,
    text: str,
    section: DocumentSection,
    document_id: str,
    chunk_index: int,
) -> Chunk:
    """
    Builds a Chunk object from chunk text and metadata.
    """

    text = text.strip()

    return Chunk(
        chunk_id=str(uuid.uuid4()),
        document_id=document_id,
        chunk_index=chunk_index,
        section=section.title,
        page_start=section.page_start,
        page_end=section.page_end,
        text=text,
        character_count=len(text),
        word_count=len(text.split()),
    )
def create_chunks(
    sections: list[DocumentSection],
    document_id: str,
) -> list[Chunk]:
    """
    Creates chunks from document sections using recursive
    semantic chunking.
    """

    chunks: list[Chunk] = []

    chunk_index = 0

    for section in sections:

        split_chunks = _recursive_split(section.text)

        split_chunks = _apply_overlap(split_chunks)

        for text in split_chunks:

            text = text.strip()

            if len(text) < MIN_CHUNK_LENGTH:
                continue

            chunks.append(
                _build_chunk(
                    text=text,
                    section=section,
                    document_id=document_id,
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

    return chunks