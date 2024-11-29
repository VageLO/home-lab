from typing import List
from os import listdir, remove
from os.path import isfile, join, splitext, abspath, basename, exists
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from sqlmodel import create_engine, SQLModel, Session, text
from ..dependencies import (
    check_file, 
    UploadFileDep,
    CheckFileDep,
)
from ..core.error import HTTPException, makeDetail
from ..core.models import ProjectFileScheme
from ..core.default_project import init_default
from ..core.triggers import (
    update_balance_on_transaction_delete,
    update_balance_on_transaction_insert,
    update_balance_on_transaction_update,
    update_to_account_balance,
)

router = APIRouter(
    prefix="/project",
    tags=["project"],
    responses={404: {"description": "Not found"}},
)

folder_path = abspath('./money_manager/files')

@router.post('/delete')
async def delete_project_file(
    file: CheckFileDep, 
    response: Response,
):
    """
    Delete database file (project) from folder
    """
    remove(file.file_path)
    response.status_code = 200
    return response

@router.post('/create')
async def create_project_file(
    file: ProjectFileScheme, 
    response: Response
):
    """
    Create database file (project) in folder. Require filename without extension
    """
    filename = splitext(basename(file.name))[0]
    file.name = f'{filename}.db'
    file_path = join(folder_path, file.name)

    if exists(file_path):
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Project already exist',
            )])

    engine = create_engine(f"sqlite:///{file_path}") 
    SQLModel.metadata.create_all(engine)

    session = Session(engine)

    session.execute(text(update_balance_on_transaction_delete))
    session.execute(text(update_balance_on_transaction_insert))
    session.execute(text(update_balance_on_transaction_update))
    session.execute(text(update_to_account_balance))

    # TODO: remove on production
    await init_default(session)

    session.commit()
    session.close()
    engine.dispose()

    response.set_cookie(key="project", value=file.name)
    response.status_code = 201
    return response

@router.post('/upload')
async def upload_project_file(
    file: UploadFileDep, 
    response: Response,
):
    """
    Save database file (project) passed by user in folder.
    """
    try:
        new_file = open(file.path, 'xb')
        new_file.write(file.content)
    except FileExistsError:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg=f"File {file.filename} already exist.",
            )])

    response.set_cookie(key="project", value=file.filename)
    response.status_code = 204
    return

@router.get('/list', response_model=List[str])
async def get_project_files() -> List[str]:
    """
    Return list of all database files in folder.
    """
    return [
        f for f in listdir(folder_path) 
        if isfile(join(folder_path, f))
        if splitext(f)[1] == '.db'
    ]

@router.post('/update')
async def update_project_file(
    file: UploadFileDep, 
    response: Response,
):
    """
    Rewrites existed database file with passed file.
    """
    ProjectFileScheme.name = file.filename
    await check_file(ProjectFileScheme)

    try:
        saved_file = open(file.path, 'wb')
        saved_file.write(file.content)
    except FileNotFoundError as err:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg=str(err),
            )])

    response.set_cookie(key="project", value=file.filename)
    response.status_code = 204
    return

@router.post('/download')
async def download_project_file(
    file: CheckFileDep,
):
    """
    Return existed file.
    """
    return FileResponse(
        path=file.file_path,
        filename=file.filename,     
    )

@router.post('/open')
async def open_project(
    file: CheckFileDep,
    response: Response,
):
    """
    Sends cookie with selected database file.
    """
    response.set_cookie(key="project", value=file.filename)
    response.status_code = 200
    return response
