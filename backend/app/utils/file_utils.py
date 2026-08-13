from fastapi import UploadFile, HTTPException, status
import uuid
from pathlib import Path

MAX_FILE_SIZE = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf"
}

def get_file_extension(filename:str)->str:
    return Path(filename).suffix.lower()

def validate_extension(filename: str):
    if "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )

    extension = get_file_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are allowed"
        )


async def validate_size(file: UploadFile):
    contents = await file.read()

    file_size = len(contents)

    await file.seek(0)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file"
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 50MB limit"
        )


async def validate_file(file: UploadFile):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file"
        )

    validate_extension(file.filename)

    await validate_size(file)

def generate_filename(filename: str)->str:
    extension=get_file_extension(filename)
    unique_id=str(uuid.uuid4())[:8]
    filename=Path(filename).stem
    return f"{unique_id}-{filename}{extension}"