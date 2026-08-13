from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DocumentSection:
    title: str
    text: str
    page_start: int
    page_end: int