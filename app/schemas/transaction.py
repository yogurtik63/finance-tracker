from datetime import datetime

from pydantic import BaseModel, field_validator

class TransactionCreate(BaseModel):
    value: int
    date: datetime

    @field_validator("value")
    def check_value(cls, value):
        if value == 0:
            raise ValueError("Value cannot be equal to zero!")
        elif abs(value) > 999_999_999_999:
            raise ValueError("You are too rich (or too broke)!")
        return value


class TransactionPublic(BaseModel):
    id: int
    value: int
    date: datetime
