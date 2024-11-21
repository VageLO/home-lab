from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.models import (
    Categories, 
    CategoryScheme, 
    update_attributes
)

router = APIRouter(
    prefix="/cagetory",
    tags=["cagetory"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create')
async def create_category(
    category: CategoryScheme,
    db: SessionDep,
    response: Response,
):
    """
    Create a category
    """
    new_category = Categories(parent_id=category.parent_id, title=category.title)
    session = db.session
    try:

    except 
