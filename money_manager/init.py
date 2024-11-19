from fastapi import FastAPI, Request, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import project, dashboard
from .logger import setupLogger

setupLogger()

app = FastAPI()

app.mount("/static", StaticFiles(directory="money_manager/static"), name="static")

app.include_router(project.router)
app.include_router(dashboard.router)

templates = Jinja2Templates(directory="money_manager/templates")

@app.get('/', response_class=HTMLResponse)
async def moneyManager(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
