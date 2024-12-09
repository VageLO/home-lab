from typing import List, Optional
import datetime
from decimal import Decimal
from fastapi import APIRouter, Response, Query
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from sqlmodel import (
    Field,
    Column,
    Enum,
    select,
)
from ..dependencies import SessionDep
from ..core.error import HTTPException, makeDetail
from ..core.utils import checkIfExist
from ..core.models import (
    Accounts,
    Categories,
    TransactionStatus,
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
    account_id: int = Field(default=None, foreign_key="Accounts.id")
    to_account_id: int = Field(default=None, foreign_key="Accounts.id")
    category_id: int = Field(default=None, foreign_key="Accounts.id")
    transaction_type: TransactionStatus = Field(
        default=None, 
        sa_column=Column(Enum(TransactionStatus)))
    date: datetime.date = Field(default=None)
    amount: Decimal = Field(default=None, decimal_places=2)
    to_amount: Decimal = Field(default=None, decimal_places=2)

@router.get('/list')
async def list_transactions(
    db: SessionDep,
    response: Response,
    account_id: Optional[int] = Query(None, title="list transactions by account"),
    category_id: Optional[int] = Query(None, title="list transactions by category"),
):
    """
    Return list of transactions:
        - all
        - by account_id
        - by category_id
    """
    session = db.session

    Transaction = aliased(Transactions, name="transaction")
    Account = aliased(Accounts, name="from_account")
    ToAccount = aliased(Accounts, name="to_account")
    Category = aliased(Categories, name="category")

    query = select(Transaction)

    if account_id is not None or category_id is not None:

        filter = []

        if account_id:
            checkIfExist(session, Accounts, account_id)
            filter.append(Transaction.account_id == account_id)

        if category_id:
            checkIfExist(session, Categories, category_id)
            filter.append(Transaction.category_id == category_id)

        query = query.outerjoin(Account, Transaction.account_id == Account.id).where(and_(*filter)).add_columns(Account)

    else:
        query = query.outerjoin(Account, Transaction.account_id == Account.id).add_columns(Account)

    query = query.outerjoin(ToAccount, Transaction.to_account_id == ToAccount.id).add_columns(ToAccount)
    query = query.outerjoin(Category, Transaction.category_id == Category.id).add_columns(Category)

    results = session.execute(query)
    transactions = results.mappings().all()
    
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

@router.post('/update')
async def update_transaction(
    transaction: TransactionUpdate,
    db: SessionDep,
):
    """
    Update data of a transaction.
    """
    session = db.session
    update_transaction = session.get(Transactions, transaction.id)

    if update_transaction is None:
        HTTPException(
            status_code=400,
            detail=[makeDetail(
                msg='Transaction not found',
            )])

    if not update_attributes(transaction, update_transaction):
        HTTPException(
            status_code=304,
            detail=[makeDetail(
                msg='Nothing to update',
            )])

    session.add(update_transaction)
    session.commit()

    session.refresh(update_transaction)

    session.close()
    db.engine.dispose()

    return update_transaction

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
            status_code=200,
            detail=[makeDetail(
                msg=f'Transactions with ID\'s {skiped} not found',
            )])

    session.close()
    db.engine.dispose()

    response.status_code = 204
    return
