from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ParsedPage:
    page_number: int
    text: str


@dataclass(slots=True, frozen=True)
class ParsedDocument:
    pages: list[ParsedPage]
    path: Path
    characters: int

    @property
    def page_count(self) -> int:
        return len(self.pages)