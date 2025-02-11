from os import path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..dependencies import SessionDep
from .account import account_list
from .transactions import transaction_list

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")

@router.get('/')
async def home(
    db: SessionDep,
    request: Request,
):
    accounts = account_list(db)
    transactions = transaction_list(
        db,
        None,
        None,
        None,
        None,
        None,
    )
    project = path.basename(db.engine.url.database)
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={
                "accounts": accounts,
                "transactions": transactions,
                "project": project,
            }
    )
