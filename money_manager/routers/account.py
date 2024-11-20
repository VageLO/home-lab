from typing_extensions import Annotated
from typing import Optional
from types import SimpleNamespace
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, validator
from ..dependencies import session
from ..core.models import Accounts

router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)

class Account(BaseModel):
    id: int = Field(None)
    title: str = Field(max_length=255)
    currency: str = Field(max_length=10)
    balance: float = Field(0)

    @validator('balance')
    def check_two_decimal(cls, v):
        if round(v, 2) != v:
            raise ValueError('Balance must have 2 digits after dot')
        return v

# TODO: UpdateAccount class
class UpdateAccount(Account):
    id: int
    title: str = Field(default=None, max_length=255)
    currency: str = Field(default=None, max_length=10)
    balance: float = Field(default=None)

@router.post('/create')
async def create_account(
    account: Account,
    db: Annotated[SimpleNamespace, Depends(session)],
    response: Response,
):
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
        raise HTTPException(status_code=400, detail=f'ERROR: {err}')

    session.refresh(save_account)

    session.close()
    db.engine.dispose()


    response.status_code = 201
    return save_account

@router.post('/update')
async def update_account(
    account: UpdateAccount,
    db: Annotated[SimpleNamespace, Depends(session)],
    response: Response,
):
    session = db.session
    update_account = session.get(Accounts, account.id)
    print(update_account)
    print(account)

    session.close()
    db.engine.dispose()
    return update_account
