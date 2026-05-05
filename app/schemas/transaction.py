from datetime import datetime, date, timezone
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from app.core.config import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class TransactionFilter(BaseModel):
    from_date: date | None = None
    to_date: date | None = None
    type: Literal["expense", "income"] | None = None
    category: str | None = None
    limit: int = 10
    offset: int = 0

    @model_validator(mode="after")
    def check_dates(self):
        if not self.from_date or not self.to_date:
            self.from_date = None
            self.to_date = None
            return self

        if self.from_date >= self.to_date:
            raise ValueError("'from' date can't be less than 'to' date!")

        return self

    @model_validator(mode="after")
    def check_category(self):
        if self.type is None or self.category is None:
            return self

        if self.type == "expense" and self.category not in EXPENSE_CATEGORIES:
            raise ValueError("Wrong 'category' path parameter")
        if self.type == "income" and self.category not in INCOME_CATEGORIES:
            raise ValueError("Wrong 'category' path parameter")

        return self

    @field_validator("limit")
    @classmethod
    def check_limit(cls, value):
        if value < 1:
            raise ValueError("Limit cannot be less than 1!")
        if value > 50:
            raise ValueError("Limit cannot be more than 50!")

        return value

    @field_validator("offset")
    @classmethod
    def check_offset(cls, value):
        if value < 0:
            raise ValueError("Offset cannot be less than 0!")
        if value > 1000:
            raise ValueError("Offset cannot be more than 1000!")

        return value

    @field_validator("from_date", "to_date", mode="before")
    @classmethod
    def parse_strict_date(cls, value):
        if value is None:
            return value

        if isinstance(value, date):
            return value

        if not isinstance(value, str):
            raise ValueError("Date must be string in YYYY-MM-DD format")

        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format, use YYYY-MM-DD")


class TransactionCreate(BaseModel):
    value: int
    date: datetime
    category: str

    @field_validator("value")
    @classmethod
    def check_value(cls, value):
        if value == 0:
            raise ValueError("Value cannot be equal to zero!")
        elif abs(value) > 999_999_999_999:
            raise ValueError("You are too rich (or too broke)!")
        return value

    @field_validator("date", mode="after")
    @classmethod
    def normalize_date(cls, value: datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def check_category(self):
        if self.value < 0 and self.category not in EXPENSE_CATEGORIES:
            raise ValueError("Wrong spend!")

        elif self.value > 0 and self.category not in INCOME_CATEGORIES:
            raise ValueError("Wrong incoming!")

        return self

class TransactionPublic(BaseModel):
    id: int
    value: int
    date: datetime
    category: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return value

class TransactionListResponse(BaseModel):
    items: list[TransactionPublic]
    count: int