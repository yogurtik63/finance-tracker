from datetime import datetime

from pydantic import BaseModel

class TransactionCreate(BaseModel):
    value: int
    date: datetime
    user_id: int

class TransactionPublic(BaseModel):
    id: int
    value: int
    date: datetime
    user_id: int
