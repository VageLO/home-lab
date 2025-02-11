from decimal import Decimal
from sqlmodel import Field, select
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Response
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
    title: str | None = Field(default=None, min_length=1, max_length=255)
    currency: str = Field(default=None, min_length=1, max_length=10)
    balance: Decimal = Field(default=None, decimal_places=2)

def account_list(db):
    session = db.session
    statement = select(Accounts).order_by(Accounts.title.asc())
    results = session.exec(statement) 
    accounts = results.all()
    
    session.close()
    db.engine.dispose()
    return accounts

def account_create(account, db):
    session = db.session
    save_account = Accounts(
        title=account.title, 
        currency=account.currency, 
        balance=account.balance,
    ) 

    try:
        session.add(save_account)
        session.commit()

    except IntegrityError:
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

    return save_account

def account_update(account, db):
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
            status_code=404, 
            detail=[makeDetail(
                msg='Nothing to update',
            )])

    try:
        session.add(update_account)
        session.commit()
    except IntegrityError:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                msg='UNIQUE constraint failed',
            )])

    session.refresh(update_account)

    session.close()
    db.engine.dispose()

    return update_account

def account_delete(id, db):
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

@router.get('/list')
async def list_accounts(
    db: SessionDep,
    response: Response,
):
    """
    Return list of all accounts
    """
    accounts = account_list(db)    
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
    save_account = account_create(account, db)
    response.status_code = 201
    return save_account

@router.post('/update')
async def update_account(
    account: AccountUpdate,
    db: SessionDep,
):
    """
    Update data of an account.
    """
    return account_update(account, db)

@router.get('/delete')
async def delete_account(
    id: int,
    db: SessionDep,
    response: Response,
):
    """
    Delete an account
    """
    account_delete(id, db)
    response.status_code = 204
    return
