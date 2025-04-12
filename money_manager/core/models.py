import enum
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import (
    Field,
    SQLModel as BaseSQLModel,
    Column,
    Enum,
    Relationship,
)

class SQLModel(BaseSQLModel):
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class TransactionStatus(str, enum.Enum):
    Withdrawal = "Withdrawal"
    Deposit = "Deposit"
    Transfer = "Transfer"

class Accounts(SQLModel, table=True):
    __tablename__ = 'Accounts'
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255)
    currency: str = Field(default=None, max_length=255)
    balance: Decimal = Field(default=0, decimal_places=2)

    transactions: List["Transactions"] = Relationship(
        cascade_delete=True,
        back_populates="transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.account_id]",
        })
    to_transactions: List["Transactions"] = Relationship(
        cascade_delete=True,
        back_populates="to_transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.to_account_id]",
        })

class Categories(SQLModel, table=True):
    __tablename__ = 'Categories'
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int]
    title: str = Field(unique=True, max_length=255)

    transactions: List["Transactions"] = Relationship(
        cascade_delete=True,
        back_populates="category",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.category_id]",
        })

class Tags(SQLModel, table=True):
    __tablename__ = 'Tags'
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255)

    transactions: List["Transactions"] = Relationship(
        back_populates="tags",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.tag_id]",
        })

class Transactions(SQLModel, table=True):
    __tablename__ = 'Transactions'

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(gt=0, foreign_key="Accounts.id", ondelete="CASCADE")
    to_account_id: Optional[int] = Field(default=None, gt=0, foreign_key="Accounts.id", ondelete="CASCADE")
    category_id: int = Field(foreign_key="Categories.id", gt=0, ondelete="CASCADE")
    tag_id: Optional[int] = Field(default=None, gt=0, foreign_key="Tags.id", ondelete="SET NULL")

    transaction_type: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus)))
    date: date
    amount: Decimal = Field(ge=0, decimal_places=2)
    to_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=255)

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
    tags: Optional[Tags] = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs = {
            "foreign_keys": "[Transactions.tag_id]",
        })

class AccountScheme(BaseModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, unique=True, max_length=255)
    currency: str = Field(min_length=1, max_length=10)
    balance: Decimal = Field(default=0, decimal_places=2)

class CategoryScheme(BaseModel):
    id: int | None = Field(default=None, primary_key=True)
    parent_id: int | None = Field(default=None)
    title: str = Field(min_length=1, unique=True, max_length=255)

class TagScheme(BaseModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, unique=True, max_length=255)

class TransactionScheme(BaseModel):
    id: int = Field(default=None, primary_key=True)
    account_id: int = Field(gt=0, foreign_key="Accounts.id")
    to_account_id: Optional[int] = Field(default=None, gt=0, foreign_key="Accounts.id")
    category_id: int = Field(gt=0, foreign_key="Categories.id")
    tag_id: Optional[int] = Field(default=None, gt=0, foreign_key="Tags.id")

    transaction_type: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus)))
    date: date
    amount: Decimal = Field(ge=0, decimal_places=2)
    to_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    description: str = Field(default=None, max_length=255)

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

        if source_value == target_value:
            continue

        setattr(target, field, source_value)
        update = True

    return update
