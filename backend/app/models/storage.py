from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class StoredFile:
    filename: str
    path: Path