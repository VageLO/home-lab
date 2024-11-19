from typing import List
from types import SimpleNamespace
from typing_extensions import Annotated
from os import listdir
from os.path import isfile, join, splitext, abspath
from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import FileResponse
from ..dependencies import upload_process, check_file

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)

folder_path = abspath('./money_manager/files')

@router.post('/upload')
async def upload_project_file(file: Annotated[SimpleNamespace, Depends(upload_process)], response: Response):
    try:
        new_file = open(file.path, 'xb')
        new_file.write(file.content)
    except FileExistsError:
        raise HTTPException(status_code=400, detail=f"File {file.filename} already exist. Want rewrite?")

    response.set_cookie(key="project", value=file.filename)
    return {'detail': f"File {file.filename} uploaded"}

@router.get('/list', response_model=List[str])
async def get_project_files() -> List[str]:
    return [
        f for f in listdir(folder_path) 
        if isfile(join(folder_path, f))
        if splitext(f)[1] == '.db'
    ]

@router.post('/update')
async def update_project_file(file: Annotated[SimpleNamespace, Depends(upload_process)], response: Response):
    try:
        saved_file = open(file.path, 'wb')
        saved_file.write(file.content)
    except FileNotFoundError as err:
        raise HTTPException(status_code=400, detail=err)

    response.set_cookie(key="project", value=file.filename)
    return {'detail': f"File {file.filename} updated"}

@router.get('/download')
async def download_project_file(file: Annotated[SimpleNamespace, Depends(check_file)]):
    return FileResponse(
        path=file.file_path,
        filename=file.filename,     
    )

@router.post('/')
async def get_cookie(file: Annotated[SimpleNamespace, Depends(check_file)], response: Response):
    response.set_cookie(key="project", value=file.filename)
    response.status_code = 200
    return response
