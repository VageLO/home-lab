from types import SimpleNamespace
from os.path import exists, splitext, join, abspath
from sqlmodel import create_engine, SQLModel, Session
from typing_extensions import Annotated
from pydantic import BaseModel
from fastapi import (
    HTTPException,
    Cookie,
    UploadFile,
    File,
    Depends,
)

class DBFile(BaseModel):
    name: str

folder_path = abspath('./money_manager/files')

async def check_cookie(project: Annotated[str, Cookie()]):
    """
    Checks if project exists with given file name in cookie
    """
    DBFile.name = project
    file = await check_file(DBFile)

    return file.file_path

async def session(
    file: Annotated[str, Depends(check_cookie)]
) -> Session:
    """
    Create session from database file (project).
    """
    engine = create_engine(f"sqlite:///{file}") 
    session = Session(engine)
    return SimpleNamespace(session=session, engine=engine)

async def upload_process(file: Annotated[UploadFile, File(...)]):
    if splitext(file.filename)[1] != '.db':
        raise HTTPException(status_code=409, detail="File extension is not .db")

    file_path = join(folder_path, file.filename)
    content = await file.read()

    return SimpleNamespace(content=content, path=file_path, filename=file.filename)

async def check_file(file: DBFile):
    """
    Checks project exists with given file name in json body
    """
    file_path = join(folder_path, file.name)

    if not exists(file_path):
        raise HTTPException(status_code=400, detail="Project not found")

    return SimpleNamespace(file_path=file_path, filename=file.name)
