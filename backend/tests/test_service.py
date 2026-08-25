from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.entities import Document
from app.database.entities import DocumentStatus
from app.database.service import DocumentService


def create_test_session():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return Session()


def create_document(
    file_hash: str = "a" * 64,
    user_id: str | None = None,
) -> Document:

    return Document(
        user_id=user_id,
        original_filename="research-paper.pdf",
        stored_filename="abc123-paper.pdf",
        parsed_filename="abc123-paper.txt",
        mime_type="application/pdf",
        file_size=1024,
        file_hash=file_hash,
        page_count=10,
        character_count=50000,
        chunk_count=50,
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_dimension=384,
        status=DocumentStatus.UPLOADED,
    )


def test_create_document():

    db = create_test_session()
    service = DocumentService(db)

    document = create_document()

    result = service.create_document(document)

    assert result.id is not None
    assert result.document_id is not None
    assert result.status == DocumentStatus.UPLOADED

    db.close()


def test_duplicate_document_is_replaced():

    db = create_test_session()
    service = DocumentService(db)

    original = service.create_document(
        create_document()
    )

    original.status = DocumentStatus.INDEXED
    original.page_count = 10

    duplicate = create_document()
    duplicate.stored_filename = "xyz789-paper.pdf"

    result = service.create_document(duplicate)

    assert result.id == original.id
    assert result.document_id == (
        original.document_id
    )
    assert result.stored_filename == (
        "xyz789-paper.pdf"
    )
    assert result.status == (
        DocumentStatus.UPLOADED
    )
    assert result.page_count == 0

    documents = service.list_documents()

    assert len(documents) == 1

    db.close()


def test_same_hash_different_users_coexist():

    db = create_test_session()
    service = DocumentService(db)

    first = service.create_document(
        create_document(user_id="1")
    )

    second = service.create_document(
        create_document(user_id="2")
    )

    assert first.id != second.id
    assert first.file_hash == second.file_hash

    assert len(
        service.list_documents(user_id="1")
    ) == 1

    assert len(
        service.list_documents(user_id="2")
    ) == 1

    db.close()


def test_duplicate_is_scoped_per_user():

    db = create_test_session()
    service = DocumentService(db)

    original = service.create_document(
        create_document(user_id="1")
    )

    duplicate = create_document(user_id="1")
    duplicate.stored_filename = "xyz789-paper.pdf"

    result = service.create_document(duplicate)

    assert result.id == original.id

    other = service.create_document(
        create_document(user_id="2")
    )

    assert other.id != original.id

    db.close()


def test_get_document():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.get_document(
        document.document_id
    )

    assert result is not None
    assert result.document_id == document.document_id

    db.close()


def test_list_documents():

    db = create_test_session()
    service = DocumentService(db)

    service.create_document(
        create_document("a" * 64)
    )

    service.create_document(
        create_document("b" * 64)
    )

    documents = service.list_documents()

    assert len(documents) == 2

    db.close()


def test_mark_parsed():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.mark_parsed(document)

    assert result.status == DocumentStatus.PARSED

    db.close()


def test_mark_chunked():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.mark_chunked(document)

    assert result.status == DocumentStatus.CHUNKED

    db.close()


def test_mark_indexing():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.mark_indexing(document)

    assert result.status == DocumentStatus.INDEXING

    db.close()


def test_mark_indexed():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.mark_indexed(document)

    assert result.status == DocumentStatus.INDEXED
    assert result.indexed_at is not None

    db.close()


def test_mark_failed():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.mark_failed(
        document,
        "Test processing error",
    )

    assert result.status == DocumentStatus.FAILED
    assert result.error_message == (
        "Test processing error"
    )

    db.close()


def test_delete_document():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    result = service.delete_document(
        document.document_id
    )

    assert result is not None
    assert result.is_deleted is True

    documents = service.list_documents()

    assert len(documents) == 0

    db.close()


def test_restore_document():

    db = create_test_session()
    service = DocumentService(db)

    document = service.create_document(
        create_document()
    )

    service.delete_document(
        document.document_id
    )

    result = service.restore_document(
        document.document_id
    )

    assert result is not None
    assert result.is_deleted is False

    documents = service.list_documents()

    assert len(documents) == 1

    db.close()