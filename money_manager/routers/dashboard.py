from typing_extensions import Annotated
from fastapi import APIRouter, UploadFile, Depends, Request
from ..dependencies import check_cookie

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(check_cookie)],
)

@router.get('/')
async def dashboard(project: Annotated[str, Depends(check_cookie)]):
    return {'detail': project}
