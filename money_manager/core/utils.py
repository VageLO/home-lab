from sqlmodel import SQLModel, Session
from ..core.error import HTTPException, makeDetail

def checkIfExist(session: Session, model: SQLModel, id: int):
    """
    Throws HTTPException if doesn't exist
    """
    obj = session.get(model, id)
    if obj is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg=f'{model.id}={id} doesn\' exist',
            )])
