from typing_extensions import Annotated
from fastapi import FastAPI, Request, Cookie, Depends, Response
from fastapi.staticfiles import StaticFiles
from .routers import project, account
from .dependencies import check_file, DBFile
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.include_router(project.router)
app.include_router(account.router)
