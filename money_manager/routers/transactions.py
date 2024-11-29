from typing import List
from fastapi import APIRouter, Response, Depends, status
from sqlmodel import Field, select
from sqlalchemy.exc import IntegrityError
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
from ..core.models import (
    Transactions,
    TransactionScheme, 
    update_attributes
)

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
    responses={404: {"description": "Not found"}},
)

class TransactionUpdate(TransactionScheme):
    id: int = Field(primary_key=True)
    title: str = Field(default=None, max_length=255)
    currency: str = Field(default=None, max_length=10)
    balance: float = Field(default=None)

@router.get('/list')
async def list_transactions(
    db: SessionDep,
    response: Response,
):
    """
    Return list of all transactions
    """
    session = db.session
    statement = select(Transactions)
    results = session.exec(statement) 
    transactions = results.all()
    
    session.close()
    db.engine.dispose()

    response.status_code = 200
    return transactions

@router.post('/create')
async def create_transaction(
    transaction: TransactionScheme,
    db: SessionDep,
    response: Response,
):
    """
    Create a transaction
    """
    session = db.session
    save_transaction = Transactions(
        account_id=transaction.account_id, 
        to_account_id=transaction.to_account_id, 
        category_id=transaction.category_id, 
        transaction_type=transaction.transaction_type, 
        date=transaction.date, 
        amount=transaction.amount, 
        to_amount=transaction.to_amount,
        description=transaction.description,
    )

    session.add(save_transaction)
    session.commit()

    session.refresh(save_transaction)

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return save_transaction

#@router.post('/update')
#async def update_transaction(
#    transaction: TransactionUpdate,
#    db: SessionDep,
#    response: Response,
#):
#    """
#    Update data of a transaction.
#    """
#    session = db.session
#    update_transaction = session.get(Transactions, transaction.id)
#
#    if update_transaction is None:
#        raise HTTPException(status_code=400, detail=f'Transaction not found')
#
#    if not update_attributes(transaction, update_transaction):
#        raise HTTPException(status_code=304, detail='Nothing to change')
#
#    try:
#        session.add(update_transaction)
#        session.commit()
#    except IntegrityError as err:
#        raise HTTPException(status_code=400, detail='UNIQUE constraint failed')
#
#    session.refresh(update_transaction)
#
#    session.close()
#    db.engine.dispose()
#
#    return update_transaction

@router.get('/delete')
async def delete_transactions(
    ids: List[int],
    db: SessionDep,
    response: Response,
):
    """
    Delete a transactions
    """
    session = db.session
    skiped = []

    for id in ids:
        transaction = session.get(Transactions, id)

        if transaction is None:
            skiped.append(id)
            continue

        session.delete(transaction)
        session.commit()

    if len(skiped) > 0:
        HTTPException(
            status_code=400, 
            detail=[makeDetail(
                type_str='select_error',
                loc=['sql exception'],
                msg=f'Transactions {skiped} not found',
            )])

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
