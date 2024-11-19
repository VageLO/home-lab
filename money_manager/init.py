from typing_extensions import Annotated
from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import project, dashboard
from .dependencies import check_file, DBFile
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.mount("/static", StaticFiles(directory="money_manager/static"), name="static")

app.include_router(project.router)
app.include_router(dashboard.router)

templates = Jinja2Templates(directory="money_manager/templates")

@app.get('/', response_class=HTMLResponse)
async def moneyManager(request: Request, project: Annotated[str | None, Cookie()] = None):
    if project is not None:
        print(project)
        file = DBFile
        file.name = project
        await check_file(file)
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
