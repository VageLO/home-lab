import random
from datetime import date
from sqlmodel import Session
from ..core.models import Accounts, Categories, Transactions

async def init_default(session: Session):
    cash_account = Accounts(title="Cash", currency="BYN", balance=100) 
    bank_account = Accounts(title="Visa", currency="USD", balance=410) 
    crypto_account = Accounts(title="BTC", currency="BTC", balance=0.3) 
    session.add(cash_account)
    session.add(bank_account)
    session.add(crypto_account)
    
    shopping = Categories(title="Shopping") 
    session.add(shopping)
    session.commit()
    session.refresh(shopping)
    session.refresh(cash_account)
    session.refresh(bank_account)
    session.refresh(crypto_account)
    shoes = Categories(parent_id=shopping.id, title="Shoes") 
    session.add(shoes)

    transactions = [cash_account, bank_account, crypto_account]
    for transaction in transactions:
        t = Transactions(
            account_id=transaction.id, 
            category_id=shopping.id,
            transaction_type="Withdrawal",
            date=date(2024, 11, 29),
            amount=round(random.uniform(1, 100), 2),
            description="desc",
        )
        session.add(t)
    session.commit()
