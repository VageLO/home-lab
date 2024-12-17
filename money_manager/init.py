from fastapi import FastAPI
from .routers import (
    project,
    account,
    categories,
    transactions,
    tags,
    import_statement,
)
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.include_router(project.router)
app.include_router(account.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(tags.router)
app.include_router(import_statement.router)
