import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def run_startup_migrations(engine: Engine) -> None:
    inspector = inspect(engine)

    if not inspector.has_table("documents"):
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("documents")
    }

    if "user_id" not in columns:
        logger.info(
            "Migration: adding user_id column to documents table"
        )

        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE documents "
                    "ADD COLUMN user_id VARCHAR(36)"
                )
            )

    indexes = inspector.get_indexes("documents")

    for index in indexes:
        if (
            index.get("unique")
            and index.get("column_names") == ["file_hash"]
        ):
            logger.info(
                "Migration: dropping global unique index on "
                "documents.file_hash (%s)",
                index["name"],
            )

            with engine.begin() as connection:
                connection.execute(
                    text(f'DROP INDEX "{index["name"]}"')
                )
