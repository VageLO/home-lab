import enum
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import (
    Field,
    SQLModel,
    Column,
    Enum,
    Relationship,
)

class TransactionStatus(str, enum.Enum):
    Withdrawal = "Withdrawal"
    Deposit = "Deposit"
    Transfer = "Transfer"

class Accounts(SQLModel, table=True):
    __tablename__ = 'Accounts'
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True)
    currency: str
    balance: Decimal = Field(default=0, decimal_places=2)

    transactions: List["Transactions"] = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.account_id]",
        })
    to_transactions: List["Transactions"] = Relationship(
        back_populates="to_transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.to_account_id]",
        })

class Categories(SQLModel, table=True):
    __tablename__ = 'Categories'
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int]
    title: str = Field(unique=True)

    transactions: List["Transactions"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.category_id]",
        })

class Transactions(SQLModel, table=True):
    __tablename__ = 'Transactions'

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="Accounts.id")
    to_account_id: Optional[int] = Field(default=None, foreign_key="Accounts.id")
    category_id: int = Field(foreign_key="Categories.id")

    transaction_type: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus)))
    date: date
    amount: Decimal = Field(decimal_places=2)
    to_amount: Decimal = Field(default=0, decimal_places=2)
    description: Optional[str]

    transactions: Optional[Accounts] = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.account_id]",
        })
    to_transactions: Optional[Accounts] = Relationship(
        back_populates="to_transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.to_account_id]",
        })
    category: Optional[Categories] = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.category_id]",
        })

class AccountScheme(BaseModel):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    currency: str = Field(max_length=10)
    balance: Decimal = Field(default=0, decimal_places=2)

class CategoryScheme(BaseModel):
    id: int = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0)
    title: str = Field(unique=True, max_length=255)

class TransactionScheme(BaseModel):
    id: int = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="Accounts.id")
    to_account_id: int = Field(default=None, foreign_key="Accounts.id")
    category_id: int = Field(foreign_key="Categories.id")
    transaction_type: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus)))
    date: date
    amount: Decimal = Field(decimal_places=2)
    to_amount: Decimal = Field(default=0, decimal_places=2)
    description: str = Field(default=None)

class ProjectFileScheme(BaseModel):
    name: str

def update_attributes(source, target) -> bool:
    field_name = "model_fields"
    update = False

    if not hasattr(source, field_name) or not hasattr(target, field_name):
        return update

    source_fields = getattr(source, field_name)
    target_fields = getattr(target, field_name)


    for field in source_fields:
        source_value = getattr(source, field)
        target_value = getattr(target, field)

        if source_value == None or source_value == target_value:
            continue

        setattr(target, field, source_value)
        update = True

    return update
