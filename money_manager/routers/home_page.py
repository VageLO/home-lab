from os import path
from typing import Optional
from fastapi import APIRouter, Query, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..dependencies import (
    SessionDep,
    CheckFileDep,
)
from .account import account_list
from .project import project_list, project_open
from .categories import categories_list
from .transactions import transaction_list

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")

@router.get('/')
async def projects(
    request: Request,
):
    """
    Display all existing projects
    """
    projects = project_list()
    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={
                "request": request,
                "projects": projects,
            }
    )

@router.post('/')
async def project_select(
    file: CheckFileDep,
    request: Request,
    response: Response,
):
    response = project_open(file, response)
    redirect_response = RedirectResponse(url=request.url_for('list_by'), status_code=302)

    if "Set-Cookie" in response.headers:
        redirect_response.headers["Set-Cookie"] = response.headers["Set-Cookie"]
    return redirect_response 

@router.get('/list')
async def list_by(
    db: SessionDep,
    request: Request,
    account_id: Optional[int] = Query(None, title="list transactions by account"),
    category_id: Optional[int] = Query(None, title="list transactions by category"),
    tag_id: Optional[int] = Query(None, title="list transactions by tag"),
    year: Optional[int] = Query(None, title="list transactions by year"),
    month: Optional[str] = Query(None, title="list transactions by month"),
):
    accounts = account_list(db)
    categories = categories_list(db)
    transactions = transaction_list(
        db,
        account_id,
        category_id,
        tag_id,
        year,
        month,
    )
    project = path.basename(db.engine.url.database)
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={
                "accounts": accounts,
                "categories": categories,
                "transactions": transactions,
                "request": request,
                "project": project,
            }
    )
