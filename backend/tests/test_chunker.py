from app.ingestion.chunking.chunker import _recursive_split


def test_recursive_split():
    text = "Hello " * 500

    chunks = _recursive_split(text)

    assert len(chunks) > 1