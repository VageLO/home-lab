import copy
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import List
from sqlmodel import Field
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Response
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
from ..core.utils import checkIfExist
from ..core.models import (
    Transactions,
    Accounts,
    Categories,
)

router = APIRouter(
    prefix="/import",
    tags=["import"],
    responses={404: {"description": "Not found"}},
)

class Import(BaseModel):
    account_id: int = Field(foreign_key="Accounts.id")
    category_id: int = Field(foreign_key="Categories.id")
    transactions: List[dict]

@router.post('/')
async def import_statement(
    statement: Import,
    db: SessionDep,
    response: Response,
):
    """
    Import transactions
    """
    session = db.session
    saved_transactions = []

    checkIfExist(session, Accounts, statement.account_id)
    checkIfExist(session, Categories, statement.category_id)

    for transaction in statement.transactions:
        save_transaction = Transactions(
            account_id=statement.account_id, 
            category_id=statement.category_id, 
            transaction_type='Withdrawal',
            date=datetime.strptime(transaction['date'], '%Y-%m-%d').date(),
            amount=Decimal(transaction['price']),
            description=transaction['description'],
        ) 

        try:
            session.add(save_transaction)
            session.commit()

        except IntegrityError:
            HTTPException(
                status_code=400, 
                detail=[makeDetail(
                    type_str='insert_error',
                    loc=['sql exception'],
                    msg='UNIQUE constraint failed',
                )])
        session.refresh(save_transaction)
        saved_transactions.append(copy.copy(save_transaction))

    account = session.get(Accounts, statement.account_id)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return { 
        "account": account,
        "transactions": saved_transactions,
    }
