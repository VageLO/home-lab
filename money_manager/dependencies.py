from types import SimpleNamespace
from os.path import exists, splitext, join, abspath
from typing_extensions import Annotated
from fastapi import HTTPException, Cookie, UploadFile, File
from pydantic import BaseModel

class DBFile(BaseModel):
    name: str

folder_path = abspath('./money_manager/files')

async def check_cookie(project: Annotated[str, Cookie()]):
    file_path = join(folder_path, project)

    if not exists(file_path):
        raise HTTPException(status_code=400, detail="Project not found")

    return file_path

async def upload_process(file: Annotated[UploadFile, File(...)]):
    if splitext(file.filename)[1] != '.db':
        raise HTTPException(status_code=409, detail="File extension is not .db")

    content = await file.read()
    file_path = join(folder_path, file.filename)
    return SimpleNamespace(content=content, path=file_path, filename=file.filename)

async def check_file(file: DBFile):
    file_path = join(folder_path, file.name)

    if not exists(file_path):
        raise HTTPException(status_code=400, detail="Project not found")

    return SimpleNamespace(file_path=file_path, filename=file.name)
