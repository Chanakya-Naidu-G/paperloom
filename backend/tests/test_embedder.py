import pytest

from app.embeddings.embedder import Embedder
from app.models.chunk import Chunk
from app.models.embeddedChunk import EmbeddedChunk


@pytest.fixture
def embedder() -> Embedder:
    return Embedder()


def test_embed_returns_correct_dimension(
    embedder: Embedder,
):

    vector = embedder.embed(
        "This is a test sentence."
    )

    assert isinstance(
        vector,
        list,
    )

    assert len(vector) == (
        embedder.config.dimension
    )


def test_embed_returns_normalized_vector(
    embedder: Embedder,
):

    vector = embedder.embed(
        "This is a test sentence."
    )

    magnitude = sum(
        value * value
        for value in vector
    )

    assert magnitude == pytest.approx(
        1.0,
        abs=1e-5,
    )


def test_embed_batch_returns_correct_count(
    embedder: Embedder,
):

    texts = [
        "This is the first sentence.",
        "This is the second sentence.",
        "This is the third sentence.",
    ]

    vectors = embedder.embed_batch(
        texts
    )

    assert len(vectors) == len(texts)

    for vector in vectors:

        assert len(vector) == (
            embedder.config.dimension
        )


def test_embed_batch_returns_normalized_vectors(
    embedder: Embedder,
):

    texts = [
        "Machine learning is useful.",
        "Artificial intelligence is growing.",
    ]

    vectors = embedder.embed_batch(
        texts
    )

    for vector in vectors:

        magnitude = sum(
            value * value
            for value in vector
        )

        assert magnitude == pytest.approx(
            1.0,
            abs=1e-5,
        )


def test_embed_batch_empty_input(
    embedder: Embedder,
):

    result = embedder.embed_batch([])

    assert result == []


def test_embed_query_returns_correct_dimension(
    embedder: Embedder,
):

    vector = embedder.embed_query(
        "What is machine learning?"
    )

    assert isinstance(
        vector,
        list,
    )

    assert len(vector) == (
        embedder.config.dimension
    )


def test_embed_query_returns_normalized_vector(
    embedder: Embedder,
):

    vector = embedder.embed_query(
        "What is machine learning?"
    )

    magnitude = sum(
        value * value
        for value in vector
    )

    assert magnitude == pytest.approx(
        1.0,
        abs=1e-5,
    )


def test_embed_chunks(
    embedder: Embedder,
):

    chunks = [
        Chunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            chunk_index=0,
            section="Introduction",
            page_start=1,
            page_end=1,
            text="This is the first chunk.",
            character_count=25,
            word_count=5,
        ),
        Chunk(
            chunk_id="chunk-2",
            document_id="doc-1",
            chunk_index=1,
            section="Introduction",
            page_start=1,
            page_end=1,
            text="This is the second chunk.",
            character_count=26,
            word_count=5,
        ),
    ]

    embedded_chunks = embedder.embed_chunks(
        chunks
    )

    assert len(embedded_chunks) == len(chunks)

    for embedded_chunk, chunk in zip(
        embedded_chunks,
        chunks,
    ):

        assert isinstance(
            embedded_chunk,
            EmbeddedChunk,
        )

        assert (
            embedded_chunk.chunk
            == chunk
        )

        assert len(
            embedded_chunk.embedding
        ) == embedder.config.dimension


def test_embed_chunks_empty_input(
    embedder: Embedder,
):

    result = embedder.embed_chunks([])

    assert result == []


def test_embed_chunks_preserves_order(
    embedder: Embedder,
):

    chunks = [
        Chunk(
            chunk_id=f"chunk-{i}",
            document_id="doc-1",
            chunk_index=i,
            section="Section",
            page_start=1,
            page_end=1,
            text=f"Chunk number {i}.",
            character_count=15,
            word_count=3,
        )
        for i in range(5)
    ]

    embedded_chunks = embedder.embed_chunks(
        chunks,
        batch_size=2,
    )

    assert [
        embedded_chunk.chunk.chunk_id
        for embedded_chunk in embedded_chunks
    ] == [
        chunk.chunk_id
        for chunk in chunks
    ]


def test_embed_chunks_with_small_batch_size(
    embedder: Embedder,
):

    chunks = [
        Chunk(
            chunk_id=f"chunk-{i}",
            document_id="doc-1",
            chunk_index=i,
            section="Section",
            page_start=1,
            page_end=1,
            text=f"This is chunk {i}.",
            character_count=18,
            word_count=4,
        )
        for i in range(7)
    ]

    embedded_chunks = embedder.embed_chunks(
        chunks,
        batch_size=2,
    )

    assert len(embedded_chunks) == 7

    for embedded_chunk in embedded_chunks:

        assert len(
            embedded_chunk.embedding
        ) == embedder.config.dimension