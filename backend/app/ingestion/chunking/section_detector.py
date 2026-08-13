import re
from dataclasses import dataclass, field



from app.models.parsed import ParsedDocument
from app.models.section import DocumentSection


KNOWN_SECTIONS = (
    "ABSTRACT",
    "INTRODUCTION",
    "BACKGROUND",
    "RELATED WORK",
    "LITERATURE REVIEW",
    "METHODS",
    "METHODOLOGY",
    "IMPLEMENTATION",
    "EXPERIMENTS",
    "EVALUATION",
    "RESULTS",
    "DISCUSSION",
    "CONCLUSION",
    "FUTURE WORK",
    "REFERENCES",
)


SECTION_PATTERN = re.compile(
    rf"""
    ^
    \s*
    (?:
        \d+(?:\.\d+)*\s+
        |
        [IVXLCDM]+\.\s+
    )?
    (?P<heading>
        {'|'.join(section.replace(' ', r'\s+') for section in KNOWN_SECTIONS)}
    )
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


@dataclass(slots=True)
class SectionBuilder:
    title: str
    page_start: int
    last_content_page: int
    lines: list[str] = field(default_factory=list)

    def build(self) -> DocumentSection:
        return DocumentSection(
            title=self.title,
            text="\n".join(self.lines).strip(),
            page_start=self.page_start,
            page_end=self.last_content_page,
        )


def normalize_heading(line: str) -> str:
    line = line.strip()

    line = re.sub(
        r"^(?:\d+(?:\.\d+)*|[IVXLCDM]+)\.\s+",
        "",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    return line.title()

def is_heading(line: str) -> str | None:
    line = line.strip()

    if not line:
        return None

    if line.startswith(
        ("•", "-", "–", "—", "*", "▪", "◦")
    ):
        return None

    normalized = re.sub(
        r"^(?:\d+(?:\.\d+)*|[IVXLCDM]+)\.\s+",
        "",
        line,
        flags=re.IGNORECASE,
    )

    match = SECTION_PATTERN.match(normalized)

    if match:
        heading = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        return heading.title()

    if looks_like_generic_heading(line):
        return line.title()

    return None
def looks_like_generic_heading(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if line.endswith(
        (".", ",", ";", ":")
    ):
        return False

    if line.startswith("(") and line.endswith(")"):
        return False

    if any(
        char in line
        for char in (
            "=",
            "+",
            "*",
            "/",
            "<",
            ">",
            "≤",
            "≥",
        )
    ):
        return False

    if len(line) > 80:
        return False

    words = line.split()

    if not 2 <= len(words) <= 10:
        return False

    if "?" in line:
        return line.lower().startswith(
            (
                "what ",
                "why ",
                "how ",
                "when ",
                "where ",
                "which ",
            )
        )

    if line.isupper():
        return True

    capitalized = sum(
        1
        for word in words
        if word and word[0].isupper()
    )

    return capitalized >= len(words) * 0.6
def detect_sections(
    document: ParsedDocument,
) -> list[DocumentSection]:

    sections: list[DocumentSection] = []

    builder = SectionBuilder(
        title="Document",
        page_start=1,
        last_content_page=1,
    )

    for page in document.pages:

        current_page = page.page_number

        lines = page.text.splitlines()

        first_meaningful_line = True

        for line in lines:

            stripped_line = line.strip()

            if not stripped_line:

                if (
                    builder.lines
                    and builder.lines[-1] != ""
                ):
                    builder.lines.append("")

                continue

            heading = is_heading(
                stripped_line
            )

            if heading is None and first_meaningful_line:
                if looks_like_generic_heading(
                    stripped_line
                ):
                    heading = normalize_heading(
                        stripped_line
                    )

            if heading:

                if builder.lines:
                    sections.append(
                        builder.build()
                    )

                builder = SectionBuilder(
                    title=heading,
                    page_start=current_page,
                    last_content_page=current_page,
                )

                first_meaningful_line = False
                continue

            builder.lines.append(
                stripped_line
            )

            builder.last_content_page = (
                current_page
            )

            first_meaningful_line = False

    if builder.lines:
        sections.append(
            builder.build()
        )

    return sections