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
    Tags,
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
    account_id: int = Field(default=None, gt=0, foreign_key="Accounts.id")
    to_account_id: int | None  = Field(default=None, gt=0, foreign_key="Accounts.id")
    category_id: int = Field(default=None, gt=0, foreign_key="Categories.id")
    tag_id: int | None = Field(default=None, gt=0, foreign_key="Tags.id")

    transaction_type: TransactionStatus = Field(
        default=None, 
        sa_column=Column(Enum(TransactionStatus)))
    date: datetime.date = Field(default=None)
    amount: Decimal = Field(default=None, ge=0, decimal_places=2)
    to_amount: Decimal = Field(default=None, ge=0, decimal_places=2)

def transaction_list(
    db,
    account_id,
    category_id,
    tag_id,
    year,
    month,
):
    session = db.session

    Transaction = aliased(Transactions, name="transaction")
    Account = aliased(Accounts, name="from_account")
    ToAccount = aliased(Accounts, name="to_account")
    Category = aliased(Categories, name="category")
    Tag = aliased(Tags, name="tag")

    query = select(Transaction)

    if (account_id is not None or
        category_id is not None or
        tag_id is not None or
        month is not None or
        year is not None):

        filter = []

        if account_id:
            checkIfExist(session, Accounts, account_id)
            filter.append(Transaction.account_id == account_id)

        if category_id:
            checkIfExist(session, Categories, category_id)
            filter.append(Transaction.category_id == category_id)

        if tag_id:
            checkIfExist(session, Tags, tag_id)
            filter.append(Transaction.tag_id == tag_id)

        if year:
            start_of_year = datetime.date(year, 1, 1)
            end_of_year = datetime.date(year, 12, 31)
            filter.append(Transaction.date >= start_of_year)
            filter.append(Transaction.date <= end_of_year)

        if month:
            year, month_num = map(int, month.split('-'))

            start_of_month = datetime.date(year, month_num, 1)
            next_month = month_num + 1 if month_num < 12 else 1
            next_year = year if month_num < 12 else year + 1
            end_of_month = datetime.date(next_year, next_month, 1)

            filter.append(Transaction.date >= start_of_month)
            filter.append(Transaction.date < end_of_month)

        query = query.outerjoin(Account, Transaction.account_id == Account.id).where(and_(*filter)).order_by(Transaction.date.desc()).add_columns(Account)

    else:
        query = query.outerjoin(Account, Transaction.account_id == Account.id).order_by(Transaction.date.desc()).add_columns(Account)

    query = query.outerjoin(ToAccount, Transaction.to_account_id == ToAccount.id).add_columns(ToAccount)
    query = query.outerjoin(Category, Transaction.category_id == Category.id).add_columns(Category)
    query = query.outerjoin(Tag, Transaction.tag_id == Tag.id).add_columns(Tag)

    results = session.execute(query)
    transactions = results.mappings().all()
    
    session.close()
    db.engine.dispose()

    return transactions

@router.get('/list')
async def list_transactions(
    db: SessionDep,
    response: Response,
    account_id: Optional[int] = Query(None, title="list transactions by account"),
    category_id: Optional[int] = Query(None, title="list transactions by category"),
    tag_id: Optional[int] = Query(None, title="list transactions by tag"),
    year: Optional[int] = Query(None, title="list transactions by year"),
    month: Optional[str] = Query(None, title="list transactions by month"),
):
    """
    Return list of transactions:
        - all
        - by account_id
        - by category_id
        - by tag_id
        - by month
        - by year
    """
    transactions = transaction_list(
        db,
        account_id,
        category_id,
        tag_id,
        year,
        month,
    )
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
        tag_id=transaction.tag_id,
        transaction_type=transaction.transaction_type,
        date=transaction.date,
        amount=transaction.amount,
        to_amount=transaction.to_amount,
        description=transaction.description,
    )

    session.add(save_transaction)
    session.commit()

    session.refresh(save_transaction)

    Transaction = aliased(Transactions, name="transaction")
    Account = aliased(Accounts, name="from_account")
    ToAccount = aliased(Accounts, name="to_account")
    Category = aliased(Categories, name="category")
    Tag = aliased(Tags, name="tag")

    query = select(Transaction).where(Transaction.id == save_transaction.id)

    query = query.outerjoin(Account, Transaction.account_id == Account.id).add_columns(Account)
    query = query.outerjoin(ToAccount, Transaction.to_account_id == ToAccount.id).add_columns(ToAccount)
    query = query.outerjoin(Category, Transaction.category_id == Category.id).add_columns(Category)
    query = query.outerjoin(Tag, Transaction.tag_id == Tag.id).add_columns(Tag)

    results = session.execute(query)
    new_transaction = results.mappings().first()

    session.close()
    db.engine.dispose()

    response.status_code = 201
    return new_transaction

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
            status_code=404,
            detail=[makeDetail(
                msg='Nothing to update',
            )])

    session.add(update_transaction)
    session.commit()

    session.refresh(update_transaction)

    Transaction = aliased(Transactions, name="transaction")
    Account = aliased(Accounts, name="from_account")
    ToAccount = aliased(Accounts, name="to_account")
    Category = aliased(Categories, name="category")
    Tag = aliased(Tags, name="tag")

    query = select(Transaction).where(Transaction.id == update_transaction.id)

    query = query.outerjoin(Account, Transaction.account_id == Account.id).add_columns(Account)
    query = query.outerjoin(ToAccount, Transaction.to_account_id == ToAccount.id).add_columns(ToAccount)
    query = query.outerjoin(Category, Transaction.category_id == Category.id).add_columns(Category)
    query = query.outerjoin(Tag, Transaction.tag_id == Tag.id).add_columns(Tag)

    results = session.execute(query)
    updated_transaction = results.mappings().first()

    session.close()
    db.engine.dispose()

    return updated_transaction

@router.post('/delete')
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
