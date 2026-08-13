from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.entities import Document, DocumentStatus
from app.database.repository import DocumentRepository


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
) -> Document:

    return Document(
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
        status=DocumentStatus.INDEXED,
    )


def test_create_document():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = create_document()

    result = repository.create(document)

    assert result.id is not None
    assert result.document_id is not None
    assert result.original_filename == "research-paper.pdf"

    db.close()


def test_get_by_document_id():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = repository.create(
        create_document()
    )

    result = repository.get_by_document_id(
        document.document_id
    )

    assert result is not None
    assert result.document_id == document.document_id

    db.close()


def test_get_by_file_hash():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = repository.create(
        create_document()
    )

    result = repository.get_by_file_hash(
        document.file_hash
    )

    assert result is not None
    assert result.file_hash == document.file_hash

    db.close()


def test_update_document():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = repository.create(
        create_document()
    )

    document.status = DocumentStatus.FAILED
    document.error_message = "Test error"

    result = repository.update(document)

    assert result.status == DocumentStatus.FAILED
    assert result.error_message == "Test error"

    db.close()


def test_list_documents():

    db = create_test_session()
    repository = DocumentRepository(db)

    document1 = create_document(
        file_hash="a" * 64
    )

    document2 = create_document(
        file_hash="b" * 64
    )

    repository.create(document1)
    repository.create(document2)

    documents = repository.list_documents()

    assert len(documents) == 2

    db.close()


def test_soft_delete():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = repository.create(
        create_document()
    )

    result = repository.soft_delete(
        document.document_id
    )

    assert result is not None
    assert result.is_deleted is True

    documents = repository.list_documents()

    assert len(documents) == 0

    db.close()


def test_include_deleted():

    db = create_test_session()
    repository = DocumentRepository(db)

    document = repository.create(
        create_document()
    )

    repository.soft_delete(
        document.document_id
    )

    documents = repository.list_documents(
        include_deleted=True
    )

    assert len(documents) == 1
    assert documents[0].is_deleted is True

    db.close()