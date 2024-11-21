from fastapi import APIRouter, Response, HTTPException
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.models import (
    Categories, 
    CategoryScheme, 
    update_attributes
)

router = APIRouter(
    prefix="/category",
    tags=["category"],
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
        session.add(new_category)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail='UNIQUE constraint failed')

    session.refresh(new_category)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return new_category
