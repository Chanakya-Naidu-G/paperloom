from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RetrievalResult:

    chunk_id: str
    document_id: str
    text: str
    distance: float
    chunk_index: int
    section: str
    page_start: int
    page_end: int
    character_count: int
    word_count: int
@dataclass(frozen=True, slots=True)
class RetrievalConfig:

    initial_candidates: int = 15

    neighbour_seeds: int = 2

    neighbours_per_seed: int = 5

    similarity_threshold: float = 0.65

    neighbour_support_bonus: float = 0.05

    max_sections: int = 5