from fastapi import APIRouter, Depends, UploadFile, File

from app.api.dependencies import get_upload_service
from app.models.response import UploadResponse
from app.services.upload_service import UploadService


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(
        get_upload_service
    ),
):

    return await upload_service.process_upload(
        file
    )