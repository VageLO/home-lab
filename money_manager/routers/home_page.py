from os import path
from typing import Optional
from fastapi import APIRouter, Query, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, HTMLResponse
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
    accounts = jsonable_encoder(account_list(db))
    categories = jsonable_encoder(categories_list(db))
    transactions = jsonable_encoder(transaction_list(
        db,
        account_id,
        category_id,
        tag_id,
        year,
        month,
    ))
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

def generate_pie(transactions):
    import matplotlib.pyplot as plt
    import mpld3
    #import numpy as np
    from collections import defaultdict
    
    category_sums = defaultdict(float)
    for entry in transactions:
        transaction = entry['transaction']
        category_title = entry['category']['title']
        amount = float(transaction['amount'])  # Convert string amount to float
        if transaction['transaction_type'] == 'Withdrawal':
            category_sums[category_title] += amount

    # Prepare data for the pie chart
    categories = list(category_sums.keys())
    amounts = list(category_sums.values())

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(amounts, wedgeprops=dict(width=0.5), startangle=-40)

    legend_labels = [f"{amt:.2f}: {cat}" for cat, amt in zip(categories, amounts)]

    ax.legend(wedges, legend_labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(0.9, 0.5),
        fontsize=10,
    )

    plt.tight_layout()

    ax.set_title("A donut") 

    html = mpld3.fig_to_html(fig)

    plt.close(fig)
    return html

@router.get('/pie', response_class=HTMLResponse)
async def pie(
    db: SessionDep,
):
    transactions = jsonable_encoder(transaction_list(db))
    return generate_pie(transactions)
