from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.database.connection import Base


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    CHUNKED = "CHUNKED"
    INDEXING = "INDEXING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        index=True,
        nullable=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    parsed_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    embedding_dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.UPLOADED,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,  # For FAILED status
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )