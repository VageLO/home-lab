from types import SimpleNamespace
from os import getenv, makedirs
from os.path import exists, splitext, join, abspath
from sqlmodel import create_engine, Session, text
from typing_extensions import Annotated
from .core.error import HTTPException, makeDetail
from .core.models import ProjectFileScheme
from fastapi import (
    Cookie,
    UploadFile,
    File,
    Depends,
)

folder_path = getenv('PROJECT_FOLDER', abspath('./money_manager/projects'))

def check_project_folder():
    if not exists(folder_path):
        makedirs(folder_path)

async def check_cookie(project: Annotated[str, Cookie()]):
    """
    Checks if project exists with given file name in cookie
    """
    ProjectFileScheme.name = project
    file = await check_file(ProjectFileScheme)

    return file.file_path

async def session(
    file: Annotated[str, Depends(check_cookie)]
) -> Session:
    """
    Create session from database file (project).
    """
    engine = create_engine(f"sqlite:///{file}") 

    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))

    session = Session(engine)
    return SimpleNamespace(session=session, engine=engine)

async def upload_process(file: Annotated[UploadFile, File(...)]):
    if splitext(file.filename)[1] != '.db':
        HTTPException(
            status_code=409, 
            detail=[makeDetail(
                msg='File extension is not .db',
            )])

    file_path = join(folder_path, file.filename)
    content = await file.read()

    return SimpleNamespace(content=content, path=file_path, filename=file.filename)

async def check_file(file: ProjectFileScheme):
    """
    Checks project exists with given file name in json body
    """
    file_path = join(folder_path, file.name)

    if not exists(file_path):
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Project not found',
            )])

    return SimpleNamespace(file_path=file_path, filename=file.name)

CheckFileDep = Annotated[SimpleNamespace, Depends(check_file)]
SessionDep = Annotated[Session, Depends(session)]
UploadFileDep = Annotated[SimpleNamespace, Depends(upload_process)]
