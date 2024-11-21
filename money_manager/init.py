from fastapi import FastAPI
from .routers import project, account
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.include_router(project.router)
app.include_router(account.router)
