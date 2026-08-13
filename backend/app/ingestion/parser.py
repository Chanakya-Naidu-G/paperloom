import fitz

from app.models.parsed import ParsedPage


def parse_pdf(file_path: str):

    document = fitz.open(file_path)

    pages = [
        ParsedPage(
            page_number=page.number + 1,
            text=page.get_text(),
        )
        for page in document
    ]

    document.close()

    return {
        "text": "\n".join(page.text for page in pages),
        "pages": pages,
    }
