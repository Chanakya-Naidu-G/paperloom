import pytest

from app.vectorstore.chroma import ChromaDB


class FakeCollection:

    def __init__(
        self,
        results=None,
        error: Exception | None = None,
    ) -> None:

        self.results = results
        self.error = error
        self.last_query = None

    def query(
        self,
        *,
        query_embeddings,
        n_results,
        where,
        include,
    ):

        self.last_query = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "where": where,
            "include": include,
        }

        if self.error is not None:
            raise self.error

        return self.results


def create_service(
    results=None,
    error: Exception | None = None,
):

    service = ChromaDB.__new__(ChromaDB)

    service._collection = FakeCollection(
        results=results,
        error=error,
    )

    return service


def make_results():

    return {
        "ids": [
            [
                "chunk-1",
                "chunk-2",
            ]
        ],
        "documents": [
            [
                "First chunk text.",
                "Second chunk text.",
            ]
        ],
        "metadatas": [
            [
                {
                    "document_id": "doc-1",
                    "chunk_index": 0,
                    "section": "Introduction",
                    "page_start": 1,
                    "page_end": 2,
                    "character_count": 18,
                    "word_count": 3,
                },
                {
                    "document_id": "doc-1",
                    "chunk_index": 1,
                    "section": "Methods",
                    "page_start": 3,
                    "page_end": 4,
                    "character_count": 19,
                    "word_count": 3,
                },
            ]
        ],
        "distances": [
            [
                0.1,
                0.2,
            ]
        ],
    }


def test_query_returns_retrieval_results():

    service = create_service(
        results=make_results()
    )

    results = service.query(
        [0.1, 0.2, 0.3, 0.4]
    )

    assert len(results) == 2

    assert results[0].chunk_id == "chunk-1"
    assert results[0].document_id == "doc-1"
    assert results[0].text == "First chunk text."
    assert results[0].distance == 0.1
    assert results[0].chunk_index == 0
    assert results[0].section == "Introduction"
    assert results[0].page_start == 1
    assert results[0].page_end == 2
    assert results[0].character_count == 18
    assert results[0].word_count == 3

    assert results[1].chunk_id == "chunk-2"
    assert results[1].document_id == "doc-1"
    assert results[1].text == "Second chunk text."
    assert results[1].distance == 0.2
    assert results[1].chunk_index == 1
    assert results[1].section == "Methods"
    assert results[1].page_start == 3
    assert results[1].page_end == 4
    assert results[1].character_count == 19
    assert results[1].word_count == 3


def test_query_passes_query_vector_correctly():

    service = create_service(
        results=make_results()
    )

    query_vector = (
        0.1,
        0.2,
        0.3,
        0.4,
    )

    service.query(
        query_vector
    )

    assert service._collection.last_query[
        "query_embeddings"
    ] == [
        [
            0.1,
            0.2,
            0.3,
            0.4,
        ]
    ]


def test_query_passes_top_k():

    service = create_service(
        results=make_results()
    )

    service.query(
        [0.1, 0.2, 0.3, 0.4],
        top_k=10,
    )

    assert (
        service._collection.last_query[
            "n_results"
        ]
        == 10
    )


def test_query_without_document_filter():

    service = create_service(
        results=make_results()
    )

    service.query(
        [0.1, 0.2, 0.3, 0.4]
    )

    assert (
        service._collection.last_query[
            "where"
        ]
        is None
    )


def test_query_with_document_filter():

    service = create_service(
        results=make_results()
    )

    document_ids = [
        "doc-1",
        "doc-2",
    ]

    service.query(
        [0.1, 0.2, 0.3, 0.4],
        document_ids=document_ids,
    )

    assert (
        service._collection.last_query[
            "where"
        ]
        == {
            "document_id": {
                "$in": document_ids
            }
        }
    )


def test_query_empty_document_filter_returns_empty():

    service = create_service(
        results=make_results()
    )

    results = service.query(
        [0.1, 0.2, 0.3, 0.4],
        document_ids=[],
    )

    assert results == []

    assert (
        service._collection.last_query
        is None
    )


def test_query_rejects_empty_vector():

    service = create_service(
        results=make_results()
    )

    with pytest.raises(
        ValueError,
        match="query_vector must not be empty",
    ):
        service.query([])


def test_query_rejects_invalid_top_k():

    service = create_service(
        results=make_results()
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero",
    ):
        service.query(
            [0.1, 0.2, 0.3, 0.4],
            top_k=0,
        )


def test_query_handles_empty_response():

    service = create_service(
        results={}
    )

    results = service.query(
        [0.1, 0.2, 0.3, 0.4]
    )

    assert results == []


def test_query_raises_runtime_error_when_store_fails():

    service = create_service(
        error=RuntimeError(
            "Chroma unavailable"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="vector store query failed",
    ):
        service.query(
            [0.1, 0.2, 0.3, 0.4]
        )


def test_query_raises_on_malformed_response():

    malformed_results = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
    }

    service = create_service(
        results=malformed_results
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid response",
    ):
        service.query(
            [0.1, 0.2, 0.3, 0.4]
        )


def test_query_raises_on_invalid_metadata():

    results = make_results()

    results["metadatas"][0][0] = "invalid"

    service = create_service(
        results=results
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid metadata",
    ):
        service.query(
            [0.1, 0.2, 0.3, 0.4]
        )


def test_query_raises_on_missing_metadata_field():

    results = make_results()

    del results["metadatas"][0][0][
        "document_id"
    ]

    service = create_service(
        results=results
    )

    with pytest.raises(KeyError):
        service.query(
            [0.1, 0.2, 0.3, 0.4]
        )


def test_query_raises_on_mismatched_result_lengths():

    results = make_results()

    results["distances"][0] = [
        0.1,
    ]

    service = create_service(
        results=results
    )

    with pytest.raises(
        RuntimeError,
        match="Inconsistent response",
    ):
        service.query(
            [0.1, 0.2, 0.3, 0.4]
        )


def test_query_requests_required_fields():

    service = create_service(
        results=make_results()
    )

    service.query(
        [0.1, 0.2, 0.3, 0.4]
    )

    assert (
        service._collection.last_query[
            "include"
        ]
        == [
            "documents",
            "metadatas",
            "distances",
        ]
    )