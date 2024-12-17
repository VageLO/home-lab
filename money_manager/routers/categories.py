from fastapi import APIRouter, Response
from sqlmodel import Field, select
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
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

class CategoryUpdate(CategoryScheme):
    id: int = Field(primary_key=True)

@router.get('/list')
async def list_categories(
    db: SessionDep,
    response: Response,
):
    """
    Return list of all categories
    """
    session = db.session
    statement = select(Categories).order_by(Categories.title.asc())
    results = session.exec(statement) 
    categories = results.all()
    
    session.close()
    db.engine.dispose()

    response.status_code = 200
    return categories

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
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg='UNIQUE constraint failed',
            )])

    session.refresh(new_category)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return new_category

@router.post('/update')
async def update_category(
    category: CategoryUpdate,
    db: SessionDep,
):
    """
    Update data of a category.
    """
    session = db.session
    update_category = session.get(Categories, category.id)

    if update_category is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Category not found',
            )])

    if not update_attributes(category, update_category):
        HTTPException(
            status_code=304, 
            detail=[makeDetail(
                msg='Nothing to update',
            )])

    try:
        session.add(update_category)
        session.commit()
    except IntegrityError:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg='UNIQUE constraint failed',
            )])

    session.refresh(update_category)

    session.close()
    db.engine.dispose()

    return update_category

@router.get('/delete')
async def delete_category(
    id: int,
    db: SessionDep,
    response: Response,
):
    """
    Delete a category
    """
    session = db.session
    category = session.get(Categories, id)

    if category is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Category not found',
            )])

    session.delete(category)
    session.commit()

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
