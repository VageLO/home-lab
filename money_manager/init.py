from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="money_manager/static"), name="static")

templates = Jinja2Templates(directory="money_manager/templates")

@app.get('/', response_class=HTMLResponse)
async def moneyManager(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.post('/project')
async def upload_project_file(file: UploadFile):
    content = await file.read()
    file_path = f'./money_manager/files/{file.filename}'

    try:
        new_file = open(file_path, 'xb')
        new_file.write(content)
    except FileExistsError:
        # TODO: make update route
        return {'message': f"file {file.filename} already exist. Want rewrite?"}

    return {'message': f"file {file.filename} saved"}
