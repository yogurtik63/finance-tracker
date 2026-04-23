from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    value: int
    date: int
    user_id: int = Field(nullable=False, foreign_key="user.id")

    user: "User" = Relationship(back_populates="transactions")
