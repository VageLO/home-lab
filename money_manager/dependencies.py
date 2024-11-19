from types import SimpleNamespace
from os.path import exists, splitext, join
from typing_extensions import Annotated
from fastapi import HTTPException, Cookie, UploadFile, File

# TODO: Fix path join
folder_path = './money_manager/files'

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

async def check_file(filename: str):
    file_path = join(folder_path, filename)

    if not exists(file_path):
        raise HTTPException(status_code=400, detail="Project not found")

    return SimpleNamespace(file_path=file_path, filename=filename)
