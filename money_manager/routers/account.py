from fastapi import APIRouter, Response, Depends
from sqlmodel import Field, select
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
from ..core.models import (
    Accounts, 
    AccountScheme, 
    update_attributes
)

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)

class AccountUpdate(AccountScheme):
    id: int = Field(primary_key=True)
    title: str = Field(default=None, max_length=255)
    currency: str = Field(default=None, max_length=10)
    balance: float = Field(default=None)

@router.get('/list')
async def list_accounts(
    db: SessionDep,
    response: Response,
):
    """
    Return list of all accounts
    """
    session = db.session
    statement = select(Accounts)
    results = session.exec(statement) 
    accounts = results.all()
    
    session.close()
    db.engine.dispose()

    response.status_code = 200
    return accounts

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
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='insert_error',
                loc=['sql exception'],
                msg='UNIQUE constraint failed',
            )])

    session.refresh(save_account)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return save_account

@router.post('/update')
async def update_account(
    account: AccountUpdate,
    db: SessionDep,
    response: Response,
):
    """
    Update data of an account.
    """
    session = db.session
    update_account = session.get(Accounts, account.id)

    if update_account is None:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Account not found',
            )])

    if not update_attributes(account, update_account):
        HTTPException(
            status_code=304, 
            detail=[makeDetail(
                msg='Nothing to change',
            )])

    try:
        session.add(update_account)
        session.commit()
    except IntegrityError as err:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='UNIQUE constraint failed',
            )])

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
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='Account not found',
            )])

    session.delete(account)
    session.commit()

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
