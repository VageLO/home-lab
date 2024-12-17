from fastapi import APIRouter, Response
from sqlmodel import Field, select
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
from ..core.models import (
    Tags, 
    TagScheme, 
    update_attributes
)

router = APIRouter(
    prefix="/tag",
    tags=["tag"],
    responses={404: {"description": "Not found"}},
)

class TagUpdate(TagScheme):
    id: int = Field(primary_key=True)

@router.get('/list')
async def list_tags(
    db: SessionDep,
    response: Response,
):
    """
    Return list of all tags
    """
    session = db.session
    statement = select(Tags)
    results = session.exec(statement) 
    tags = results.all()
    
    session.close()
    db.engine.dispose()

    response.status_code = 200
    return tags

@router.post('/create')
async def create_tag(
    tag: TagScheme,
    db: SessionDep,
    response: Response,
):
    """
    Create a tag
    """
    new_tag = Tags(title=tag.title)
    session = db.session

    try:
        session.add(new_tag)
        session.commit()
    except IntegrityError:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg='UNIQUE constraint failed',
            )])

    session.refresh(new_tag)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return new_tag

@router.post('/update')
async def update_tag(
    tag: TagUpdate,
    db: SessionDep,
):
    """
    Update data of a tag.
    """
    session = db.session
    update_tag = session.get(Tags, tag.id)

    if update_tag is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Tag not found',
            )])

    if not update_attributes(tag, update_tag):
        HTTPException(
            status_code=304, 
            detail=[makeDetail(
                msg='Nothing to update',
            )])

    try:
        session.add(update_tag)
        session.commit()
    except IntegrityError:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg='UNIQUE constraint failed',
            )])

    session.refresh(update_tag)

    session.close()
    db.engine.dispose()

    return update_tag

@router.get('/delete')
async def delete_tag(
    id: int,
    db: SessionDep,
    response: Response,
):
    """
    Delete a tag
    """
    session = db.session
    tag = session.get(Tags, id)

    if tag is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Tag not found',
            )])

    session.delete(tag)
    session.commit()

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
