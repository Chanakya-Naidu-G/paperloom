from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.entities import Document


class DocumentRepository:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self._db = db

    def create(
        self,
        document: Document,
    ) -> Document:

        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)

        return document

    def get_by_document_id(
        self,
        document_id: str,
        include_deleted: bool = False,
    ) -> Document | None:

        statement = select(Document).where(
            Document.document_id == document_id
        )

        if not include_deleted:
            statement = statement.where(
                Document.is_deleted.is_(False)
            )

        return self._db.scalar(statement)
    def get_by_file_hash(
        self,
        file_hash: str,
        include_deleted: bool = False,
    ) -> Document | None:

        statement = select(Document).where(
            Document.file_hash == file_hash
        )

        if not include_deleted:
            statement = statement.where(
                Document.is_deleted.is_(False)
            )

        return self._db.scalar(statement)

    def list_documents(
        self,
        include_deleted: bool = False,
    ) -> list[Document]:

        statement = select(Document)

        if not include_deleted:
            statement = statement.where(
                Document.is_deleted.is_(False)
            )

        statement = statement.order_by(
            Document.uploaded_at.desc()
        )

        return list(
            self._db.scalars(statement).all()
        )

    def update(
        self,
        document: Document,
    ) -> Document:

        self._db.commit()
        self._db.refresh(document)

        return document

    def soft_delete(
        self,
        document_id: str,
    ) -> Document | None:

        document = self.get_by_document_id(
            document_id
        )

        if document is None:
            return None

        document.is_deleted = True

        self._db.commit()
        self._db.refresh(document)

        return document
    def restore(
    self,
    document_id: str,
    ) -> Document | None:

        document = self.get_by_document_id(
            document_id,
            include_deleted=True,
        )

        if document is None:
            return None

        document.is_deleted = False

        try:
            self._db.commit()
            self._db.refresh(document)

            return document

        except Exception:
            self._db.rollback()
            raise