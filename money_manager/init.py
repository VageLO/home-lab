from fastapi import FastAPI
from .routers import project, account, categories, transactions
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.include_router(project.router)
app.include_router(account.router)
app.include_router(categories.router)
app.include_router(transactions.router)
