from app.embeddings.embedder import Embedder
from app.models.retrieval import RetrievalResult
from app.vectorstore.base import VectorStore


INITIAL_CANDIDATES = 15
NEIGHBOUR_SEEDS = 2
NEIGHBOURS_PER_SEED = 5

SIMILARITY_THRESHOLD = 0.65
NEIGHBOUR_SUPPORT_BONUS = 0.05

LEXICAL_BONUS = 0.08
SECTION_MATCH_BONUS = 0.08
EXACT_PHRASE_BONUS = 0.10

STOP_WORDS = {
    "what",
    "is",
    "a",
    "an",
    "the",
    "of",
    "in",
    "on",
    "for",
    "to",
    "and",
    "or",
    "are",
    "was",
    "were",
    "how",
    "does",
    "do",
}

class RetrievalService:

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
    ) -> None:

        self._embedder = embedder
        self._vector_store = vector_store

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:

        self._validate_query(
            query,
            top_k,
        )

        query_vector = self._embedder.embed_query(
            query
        )

        candidates = self._initial_search(
            query_vector,
            document_ids,
        )

        if not self._should_expand(
            candidates,
            top_k,
        ):
            candidates = self._deduplicate(
                candidates
            )

            candidates = self._rerank(
                candidates,
                query
            )

            return candidates[:top_k]

        expanded_candidates, support_counts = (
            self._expand_candidates(
                candidates,
                query_vector,
                document_ids,
            )
        )

        candidates = self._merge_candidates(
            candidates,
            expanded_candidates,
        )

        candidates = self._deduplicate(
            candidates
        )

        candidates = self._rerank(
            candidates,
            query,
            support_counts,
        )

        return candidates[:top_k]

    def _validate_query(
        self,
        query: str,
        top_k: int,
    ) -> None:

        if not query.strip():
            raise ValueError(
                "query must not be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

    def _initial_search(
        self,
        query_vector: list[float],
        document_ids: list[str] | None,
    ) -> list[RetrievalResult]:

        return self._vector_store.query(
            query_vector,
            top_k=INITIAL_CANDIDATES,
            document_ids=document_ids,
        )

    def _should_expand(
        self,
        candidates: list[RetrievalResult],
        top_k: int,
    ) -> bool:

        if not candidates:
            return True

        top_candidates = candidates[:top_k]

        if len(top_candidates) < top_k:
            return True

        return not all(
            self._similarity(candidate)
            >= SIMILARITY_THRESHOLD
            for candidate in top_candidates
        )

    def _expand_candidates(
        self,
        candidates: list[RetrievalResult],
        query_vector: list[float],
        document_ids: list[str] | None,
    ) -> tuple[
        list[RetrievalResult],
        dict[str, int],
    ]:

        seeds = candidates[
            :NEIGHBOUR_SEEDS
        ]

        expanded: list[RetrievalResult] = []

        support_counts: dict[str, int] = {}

        for seed in seeds:

            seed_embedding = (
                self._vector_store.get_embedding(
                    seed.chunk_id
                )
            )

            if seed_embedding is None:
                continue

            neighbours = self._vector_store.query(
                seed_embedding,
                top_k=NEIGHBOURS_PER_SEED,
                document_ids=document_ids,
            )

            for neighbour in neighbours:

                if neighbour.chunk_id == seed.chunk_id:
                    continue

                expanded.append(
                    neighbour
                )

                support_counts[
                    neighbour.chunk_id
                ] = (
                    support_counts.get(
                        neighbour.chunk_id,
                        0,
                    )
                    + 1
                )

        return expanded, support_counts

    def _merge_candidates(
        self,
        candidates: list[RetrievalResult],
        expanded: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        merged: dict[
            str,
            RetrievalResult,
        ] = {}

        for candidate in candidates:
            merged[candidate.chunk_id] = candidate

        for candidate in expanded:

            if candidate.chunk_id not in merged:
                merged[
                    candidate.chunk_id
                ] = candidate

        return list(
            merged.values()
        )

    def _deduplicate(
        self,
        candidates: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        unique: dict[
            str,
            RetrievalResult,
        ] = {}

        for candidate in candidates:

            existing = unique.get(
                candidate.chunk_id
            )

            if existing is None:
                unique[
                    candidate.chunk_id
                ] = candidate
                continue

            if (
                self._similarity(candidate)
                > self._similarity(existing)
            ):
                unique[
                    candidate.chunk_id
                ] = candidate

        return list(
            unique.values()
        )

    def _rerank(
        self,
        candidates: list[RetrievalResult],
        query: str,
        support_counts: dict[str, int] | None = None,
    ) -> list[RetrievalResult]:

        support_counts = (
            support_counts or {}
        )

        return sorted(
            candidates,
            key=lambda candidate: (
                self._similarity(candidate)
                + self._lexical_bonus(
                    query,
                    candidate,
                )
                + self._support_bonus(
                    candidate,
                    support_counts,
                )
            ),
            reverse=True,
        )

    @staticmethod
    def _lexical_bonus(
        query: str,
        candidate: RetrievalResult,
    ) -> float:

        query_words = {
            word.lower().strip(".,!?;:()[]{}")
            for word in query.split()
            if len(word) > 2
            and word.lower().strip(".,!?;:()[]{}")
            not in STOP_WORDS
        }

        text = candidate.text.lower()
        section = candidate.section.lower()

        if not query_words:
            return 0.0

        matches = sum(
            1
            for word in query_words
            if word in text
        )

        bonus = (
            LEXICAL_BONUS
            * matches
            / len(query_words)
        )

        if any(
            word in section
            for word in query_words
        ):
            bonus += SECTION_MATCH_BONUS

        normalized_query = " ".join(
            query.lower().split()
        )

        normalized_text = " ".join(
            candidate.text.lower().split()
        )

        if normalized_query in normalized_text:
            bonus += EXACT_PHRASE_BONUS

        return bonus

    @staticmethod
    def _support_bonus(
        candidate: RetrievalResult,
        support_counts: dict[str, int],
    ) -> float:

        support_count = support_counts.get(
            candidate.chunk_id,
            0,
        )

        if support_count <= 1:
            return 0.0

        return (
            NEIGHBOUR_SUPPORT_BONUS
            * (support_count - 1)
        )

    def _section_first_select(
        self,
        candidates: list[RetrievalResult],
        top_k: int,
    ) -> list[RetrievalResult]:

        if not candidates:
            return []

        section_scores: dict[
            tuple[str, str],
            float,
        ] = {}

        for candidate in candidates:

            section_key = (
                candidate.document_id,
                candidate.section,
            )

            score = self._similarity(
                candidate
            )

            section_scores[
                section_key
            ] = (
                section_scores.get(
                    section_key,
                    0.0,
                )
                + score
            )

        ranked_sections = sorted(
            section_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        selected: list[RetrievalResult] = []
        used_chunks: set[str] = set()

        for section_key, _ in ranked_sections:

            if len(selected) >= top_k:
                break

            section_candidates = [
                candidate
                for candidate in candidates
                if (
                    candidate.document_id,
                    candidate.section,
                ) == section_key
                and candidate.chunk_id
                not in used_chunks
            ]

            if not section_candidates:
                continue

            best = max(
                section_candidates,
                key=self._similarity,
            )

            selected.append(best)

            used_chunks.add(
                best.chunk_id
            )

        if len(selected) < top_k:

            remaining = sorted(
                (
                    candidate
                    for candidate in candidates
                    if candidate.chunk_id
                    not in used_chunks
                ),
                key=self._similarity,
                reverse=True,
            )

            for candidate in remaining:

                if len(selected) >= top_k:
                    break

                selected.append(candidate)

                used_chunks.add(
                    candidate.chunk_id
                )

        return selected
    @staticmethod
    def _similarity(
        result: RetrievalResult,
    ) -> float:

        return 1.0 - result.distance