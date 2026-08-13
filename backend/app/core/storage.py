import os
from pathlib import Path


def _env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default))


STORAGE_ROOT = _env_path("STORAGE_ROOT", "data")

UPLOAD_DIR = STORAGE_ROOT / "uploads"
PARSED_DIR = STORAGE_ROOT / "parsed"
CHUNK_DIR = STORAGE_ROOT / "chunks"


def ensure_storage_dirs() -> None:
    for directory in (UPLOAD_DIR, PARSED_DIR, CHUNK_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def get_upload_path(filename: str) -> Path:
    return UPLOAD_DIR / filename


def get_parsed_path(filename: str) -> Path:
    return PARSED_DIR / filename


def get_chunk_path(filename: str) -> Path:
    return CHUNK_DIR / filename
