import pytest

from app.models.retrieval import RetrievalResult
from app.retrieval.service import RetrievalService


class FakeEmbedder:

    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(
        self,
        query: str,
    ) -> list[float]:

        self.queries.append(query)

        return [
            0.1,
            0.2,
            0.3,
            0.4,
        ]


class FakeVectorStore:

    def __init__(
        self,
        results: list[RetrievalResult] | None = None,
        embeddings: dict[str, list[float]] | None = None,
        neighbours: dict[
            tuple[float, ...],
            list[RetrievalResult],
        ] | None = None,
    ) -> None:

        self.results = results or []
        self.embeddings = embeddings or {}
        self.neighbours = neighbours or {}

        self.queries: list[
            tuple[
                list[float],
                int,
                list[str] | None,
            ]
        ] = []

        self.embedding_requests: list[str] = []

    def query(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:

        self.queries.append(
            (
                query_vector,
                top_k,
                document_ids,
            )
        )

        key = tuple(query_vector)

        if key in self.neighbours:

            results = self.neighbours[key]

        else:

            results = self.results

        if document_ids is not None:

            results = [
                result
                for result in results
                if result.document_id in document_ids
            ]

        return results[:top_k]

    def get_embedding(
        self,
        chunk_id: str,
    ) -> list[float] | None:

        self.embedding_requests.append(
            chunk_id
        )

        return self.embeddings.get(
            chunk_id
        )


def make_result(
    chunk_id: str,
    document_id: str,
    distance: float,
    *,
    section: str = "Introduction",
    chunk_index: int = 0,
) -> RetrievalResult:

    return RetrievalResult(
        chunk_id=chunk_id,
        document_id=document_id,
        text=f"Text for {chunk_id}",
        distance=distance,
        chunk_index=chunk_index,
        section=section,
        page_start=1,
        page_end=1,
        character_count=20,
        word_count=4,
    )


def make_service(
    results: list[RetrievalResult] | None = None,
    embeddings: dict[str, list[float]] | None = None,
    neighbours: dict[
        tuple[float, ...],
        list[RetrievalResult],
    ] | None = None,
):

    embedder = FakeEmbedder()

    vector_store = FakeVectorStore(
        results=results,
        embeddings=embeddings,
        neighbours=neighbours,
    )

    service = RetrievalService(
        embedder=embedder,
        vector_store=vector_store,
    )

    return (
        service,
        embedder,
        vector_store,
    )


def make_high_quality_results(
    count: int = 15,
) -> list[RetrievalResult]:

    sections = [
        "Introduction",
        "Background",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
    ]

    return [
        make_result(
            chunk_id=f"chunk-{i}",
            document_id="doc-1",
            distance=0.1 + (i * 0.01),
            section=sections[i % len(sections)],
            chunk_index=i,
        )
        for i in range(count)
    ]


def test_search_embeds_query():

    results = make_high_quality_results()

    service, embedder, vector_store = (
        make_service(results)
    )

    service.search(
        "What is machine learning?"
    )

    assert embedder.queries == [
        "What is machine learning?"
    ]

    assert vector_store.queries[0][0] == [
        0.1,
        0.2,
        0.3,
        0.4,
    ]


def test_initial_search_requests_fifteen_candidates():

    results = make_high_quality_results()

    service, _, vector_store = (
        make_service(results)
    )

    service.search(
        "What is AI?",
        top_k=5,
    )

    assert vector_store.queries[0][1] == 15


def test_search_passes_document_filter():

    results = make_high_quality_results()

    service, _, vector_store = (
        make_service(results)
    )

    document_ids = [
        "doc-1",
        "doc-2",
    ]

    service.search(
        "What is AI?",
        document_ids=document_ids,
    )

    assert vector_store.queries[0][2] == document_ids


def test_search_without_document_filter():

    results = make_high_quality_results()

    service, _, vector_store = (
        make_service(results)
    )

    service.search(
        "What is AI?"
    )

    assert vector_store.queries[0][2] is None


def test_search_rejects_empty_query():

    service, _, vector_store = (
        make_service()
    )

    with pytest.raises(
        ValueError,
        match="query must not be empty",
    ):

        service.search("")

    assert vector_store.queries == []


def test_search_rejects_whitespace_query():

    service, _, vector_store = (
        make_service()
    )

    with pytest.raises(
        ValueError,
        match="query must not be empty",
    ):

        service.search("   ")

    assert vector_store.queries == []


def test_search_rejects_invalid_top_k():

    service, _, vector_store = (
        make_service()
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero",
    ):

        service.search(
            "What is AI?",
            top_k=0,
        )

    assert vector_store.queries == []


def test_does_not_expand_when_top_k_scores_pass_threshold():

    results = make_high_quality_results()

    service, _, vector_store = (
        make_service(results)
    )

    retrieved = service.search(
        "What is AI?",
        top_k=5,
    )

    assert len(retrieved) == 5

    assert len(
        vector_store.embedding_requests
    ) == 0

    assert len(
        vector_store.queries
    ) == 1


def test_expands_when_top_k_scores_fail_threshold():

    initial_results = [
        make_result(
            "seed-1",
            "doc-1",
            0.2,
        ),
        make_result(
            "seed-2",
            "doc-1",
            0.3,
        ),
        make_result(
            "weak-1",
            "doc-1",
            0.8,
        ),
        make_result(
            "weak-2",
            "doc-1",
            0.85,
        ),
        make_result(
            "weak-3",
            "doc-1",
            0.9,
        ),
    ]

    seed_1_vector = [
        0.5,
        0.1,
        0.2,
        0.3,
    ]

    seed_2_vector = [
        0.6,
        0.1,
        0.2,
        0.3,
    ]

    neighbours_1 = [
        make_result(
            "neighbour-1",
            "doc-1",
            0.2,
        ),
        make_result(
            "neighbour-2",
            "doc-1",
            0.3,
        ),
    ]

    neighbours_2 = [
        make_result(
            "neighbour-3",
            "doc-1",
            0.25,
        ),
        make_result(
            "neighbour-4",
            "doc-1",
            0.35,
        ),
    ]

    embeddings = {
        "seed-1": seed_1_vector,
        "seed-2": seed_2_vector,
    }

    neighbours = {
        tuple(seed_1_vector): neighbours_1,
        tuple(seed_2_vector): neighbours_2,
    }

    service, _, vector_store = make_service(
        results=initial_results,
        embeddings=embeddings,
        neighbours=neighbours,
    )

    service.search(
        "What is AI?",
        top_k=5,
    )

    assert vector_store.embedding_requests == [
        "seed-1",
        "seed-2",
    ]

    assert len(
        vector_store.queries
    ) == 3


def test_expansion_uses_only_two_best_seeds():

    initial_results = [
        make_result(
            "seed-1",
            "doc-1",
            0.1,
        ),
        make_result(
            "seed-2",
            "doc-1",
            0.2,
        ),
        make_result(
            "seed-3",
            "doc-1",
            0.3,
        ),
        make_result(
            "weak-1",
            "doc-1",
            0.8,
        ),
        make_result(
            "weak-2",
            "doc-1",
            0.9,
        ),
    ]

    embeddings = {
        "seed-1": [0.5, 0.1, 0.2, 0.3],
        "seed-2": [0.6, 0.1, 0.2, 0.3],
        "seed-3": [0.7, 0.1, 0.2, 0.3],
    }

    neighbours = {
        (0.5, 0.1, 0.2, 0.3): [],
        (0.6, 0.1, 0.2, 0.3): [],
        (0.7, 0.1, 0.2, 0.3): [],
    }

    service, _, vector_store = make_service(
        results=initial_results,
        embeddings=embeddings,
        neighbours=neighbours,
    )

    service.search(
        "What is AI?",
        top_k=5,
    )

    assert vector_store.embedding_requests == [
        "seed-1",
        "seed-2",
    ]


def test_neighbours_are_threshold_filtered():

    initial_results = [
        make_result(
            "seed-1",
            "doc-1",
            0.2,
        ),
        make_result(
            "seed-2",
            "doc-1",
            0.3,
        ),
        make_result(
            "weak-1",
            "doc-1",
            0.8,
        ),
        make_result(
            "weak-2",
            "doc-1",
            0.85,
        ),
        make_result(
            "weak-3",
            "doc-1",
            0.9,
        ),
    ]

    seed_vector = [
        0.5,
        0.1,
        0.2,
        0.3,
    ]

    neighbours = [
        make_result(
            "good-neighbour",
            "doc-1",
            0.2,
        ),
        make_result(
            "bad-neighbour",
            "doc-1",
            0.9,
        ),
    ]

    embeddings = {
        "seed-1": seed_vector,
        "seed-2": seed_vector,
    }

    neighbour_map = {
        tuple(seed_vector): neighbours,
    }

    service, _, _ = make_service(
        results=initial_results,
        embeddings=embeddings,
        neighbours=neighbour_map,
    )

    retrieved = service.search(
        "What is AI?",
        top_k=5,
    )

    chunk_ids = {
        result.chunk_id
        for result in retrieved
    }

    assert "good-neighbour" in chunk_ids
    assert "bad-neighbour" not in chunk_ids


def test_duplicate_neighbour_is_deduplicated():

    initial_results = [
        make_result(
            "seed-1",
            "doc-1",
            0.2,
        ),
        make_result(
            "seed-2",
            "doc-1",
            0.3,
        ),
        make_result(
            "weak-1",
            "doc-1",
            0.8,
        ),
        make_result(
            "weak-2",
            "doc-1",
            0.85,
        ),
        make_result(
            "weak-3",
            "doc-1",
            0.9,
        ),
    ]

    shared = make_result(
        "shared-neighbour",
        "doc-1",
        0.2,
    )

    seed_1_vector = [
        0.5,
        0.1,
        0.2,
        0.3,
    ]

    seed_2_vector = [
        0.6,
        0.1,
        0.2,
        0.3,
    ]

    embeddings = {
        "seed-1": seed_1_vector,
        "seed-2": seed_2_vector,
    }

    neighbours = {
        tuple(seed_1_vector): [shared],
        tuple(seed_2_vector): [shared],
    }

    service, _, _ = make_service(
        results=initial_results,
        embeddings=embeddings,
        neighbours=neighbours,
    )

    retrieved = service.search(
        "What is AI?",
        top_k=5,
    )

    shared_results = [
        result
        for result in retrieved
        if result.chunk_id == "shared-neighbour"
    ]

    assert len(shared_results) <= 1


def test_search_returns_empty_when_no_candidates():

    service, _, vector_store = (
        make_service([])
    )

    results = service.search(
        "What is AI?"
    )

    assert results == []

    assert len(
        vector_store.queries
    ) == 1


def test_section_first_selection_prefers_strong_sections():

    candidates = [
        make_result(
            "chunk-a1",
            "doc-1",
            0.2,
            section="Introduction",
        ),
        make_result(
            "chunk-a2",
            "doc-1",
            0.25,
            section="Introduction",
        ),
        make_result(
            "chunk-b1",
            "doc-1",
            0.1,
            section="Methods",
        ),
        make_result(
            "chunk-c1",
            "doc-1",
            0.5,
            section="Conclusion",
        ),
    ]

    service, _, _ = make_service(
        candidates
    )

    selected = service._section_first_select(
        candidates,
        top_k=2,
    )

    assert len(selected) == 2

    assert {
        result.section
        for result in selected
    } == {
        "Introduction",
        "Methods",
    }


def test_final_results_are_limited_to_top_k():

    results = make_high_quality_results(
        count=15
    )

    service, _, _ = make_service(
        results
    )

    retrieved = service.search(
        "What is AI?",
        top_k=3,
    )

    assert len(retrieved) == 3