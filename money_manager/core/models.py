from typing import Optional
from pydantic import BaseModel, validator
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

class AccountScheme(BaseModel):
    id: int = Field(None)
    title: str = Field(max_length=255)
    currency: str = Field(max_length=10)
    balance: float = Field(0)

    @validator('balance')
    def check_two_decimal(cls, v):
        if round(v, 2) != v:
            raise ValueError('Balance must have 2 digits after dot')
        return v

class UpdateAccountScheme(AccountScheme):
    id: int
    title: str = Field(default=None, max_length=255)
    currency: str = Field(default=None, max_length=10)
    balance: float = Field(default=None)

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
