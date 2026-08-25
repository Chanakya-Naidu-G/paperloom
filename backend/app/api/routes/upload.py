from fastapi import APIRouter, Depends, UploadFile, File

from app.api.dependencies import get_upload_service
from app.auth.dependencies import get_current_user
from app.database.entities import User
from app.models.response import UploadResponse
from app.services.upload_service import UploadService


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    upload_service: UploadService = Depends(
        get_upload_service
    ),
):

    return await upload_service.process_upload(
        file,
        user_id=str(current_user.id),
    )
