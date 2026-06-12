from fastapi import APIRouter, Depends, UploadFile

from app.core.deps import get_current_user
from app.models.user import User
from app.services.upload import save_upload_file

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    url = await save_upload_file(file)
    return {"url": url}
