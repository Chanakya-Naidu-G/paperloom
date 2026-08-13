import re

from app.models.parsed import ParsedDocument, ParsedPage


def preprocess_text(text: str) -> str:
    """
    Cleans extracted text while preserving structure.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Remove trailing spaces
    text = "\n".join(
        line.strip()
        for line in text.split("\n")
    )

    # Collapse excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Remove leading/trailing whitespace
    return text.strip()


def preprocess_document(
    document: ParsedDocument
) -> ParsedDocument:
    """
    Applies preprocessing to every page.
    """

    processed_pages = []

    for page in document.pages:

        processed_pages.append(
            ParsedPage(
                page_number=page.page_number,
                text=preprocess_text(page.text)
            )
        )

    return ParsedDocument(
        pages=processed_pages,
        path=document.path,
        characters=sum(
            len(page.text)
            for page in processed_pages
        )
    )