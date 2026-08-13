from app.database.connection import SessionLocal
from app.database.service import DocumentService
from app.vectorstore.chroma import ChromaDB


DOCUMENT_ID = "cb6e8d7a-18c9-468a-8ce9-196a2d5eebf7"


db = SessionLocal()

try:
    document_service = DocumentService(db)
    vector_store = ChromaDB()

    document = document_service.delete_document(
        DOCUMENT_ID
    )

    if document is None:
        print("Document not found in database.")
    else:
        print(
            "Soft-deleted document:",
            document.document_id,
        )

    vector_store.delete_document(
        DOCUMENT_ID
    )

    print(
        "Deleted document vectors from Chroma."
    )

finally:
    db.close()