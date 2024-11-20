from typing import Optional
from sqlmodel import Field, SQLModel

class Accounts(SQLModel, table=True):
    __tablename__ = 'Accounts'
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True)
    currency: str
    balance: float = Field(default=0)

class Categories(SQLModel, table=True):
    __tablename__ = 'Categories'
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int]
    title: str = Field(unique=True)

class Transactions(SQLModel, table=True):
    __tablename__ = 'Transactions'
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="Accounts.id")
    to_account_id: Optional[int] = Field(default=None, foreign_key="Accounts.id")
    category_id: int = Field(foreign_key="Categories.id")
    transaction_type: str
    date: str
    amount: float
    to_amount: Optional[float]
    description: Optional[str]
