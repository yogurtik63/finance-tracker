from datetime import datetime
from calendar import monthrange

from pydantic import BaseModel, field_validator, model_validator

from app.core.config import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class TransactionFilter(BaseModel):
    year: int | None = None
    month: int | None = None
    day: int | None = None
    type: str | None = None
    category: str | None = None
    limit: int = 10
    offset: int = 0

    @field_validator("year")
    def check_year(cls, value):
        if value is None:
            return value

        if not (2010 <= value <= 2027):
            raise ValueError("Wrong 'year' path parameter")
        return value

    @field_validator("month")
    def check_month(cls, value):
        if value is None:
            return value

        if not (1 <= value <= 12):
            raise ValueError("Wrong 'month' path parameter")
        return value

    @model_validator(mode="after")
    def check_day(self):
        if self.year is None or self.month is None or self.day is None:
            return self

        if self.year and self.month and self.day:
            max_day = monthrange(self.year, self.month)[1]

            if not (1 <= self.day <= max_day):
                raise ValueError("Wrong day")

        return self
    @field_validator("type")
    def check_type(cls, value):
        if value is None:
            return value

        if value not in ("expense", "income"):
            raise ValueError("Wrong 'type' path parameter")
        return value

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
    def check_limit(cls, value):
        value = max(1, min(value, 50))

        return value

    @field_validator("offset")
    def check_offset(cls, value):
        value = max(0, min(value, 100))

        return value


class TransactionCreate(BaseModel):
    value: int
    date: datetime
    category: str

    @field_validator("value")
    def check_value(cls, value):
        if value == 0:
            raise ValueError("Value cannot be equal to zero!")
        elif abs(value) > 999_999_999_999:
            raise ValueError("You are too rich (or too broke)!")
        return value

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
