from typing_extensions import Annotated
from typing import Optional
from types import SimpleNamespace
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, validator
from ..dependencies import SessionDep
from ..core.models import (
    Accounts, 
    AccountScheme, 
    UpdateAccountScheme,
    update_attributes
)

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)

@router.post('/create')
async def create_account(
    account: AccountScheme,
    db: SessionDep,
    response: Response,
):
    """
    Create an account
    """
    session = db.session
    save_account = Accounts(
        title=account.title, 
        currency=account.currency, 
        balance=account.balance,
    ) 

    try:
        session.add(save_account)
        session.commit()

    except IntegrityError as err:
        raise HTTPException(status_code=400, detail='UNIQUE constraint failed')

    session.refresh(save_account)

    session.close()
    db.engine.dispose()


    response.status_code = 201
    return save_account

@router.post('/update')
async def update_account(
    account: UpdateAccountScheme,
    db: SessionDep,
    response: Response,
):
    """
    Update data of an account.
    """
    session = db.session
    update_account = session.get(Accounts, account.id)

    if update_account is None:
        raise HTTPException(status_code=400, detail=f'Account not found')

    if not update_attributes(account, update_account):
        raise HTTPException(status_code=304, detail='Nothing to change')

    try:
        session.add(update_account)
        session.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=400, detail='UNIQUE constraint failed')

    session.refresh(update_account)

    session.close()
    db.engine.dispose()

    return update_account

@router.get('/delete')
async def delete_account(
    id: int,
    db: SessionDep,
    response: Response,
):
    """
    Delete an account
    """
    session = db.session
    account = session.get(Accounts, id)

    if account is None:
        raise HTTPException(status_code=400, detail=f'Account not found')

    session.delete(account)
    session.commit()

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
