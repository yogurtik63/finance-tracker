from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .transaction import Transaction
    print(Transaction)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, index=True, unique=True)
    hash_password: str = Field(nullable=False)
    transactions: list["Transaction"] = Relationship(back_populates="user")
