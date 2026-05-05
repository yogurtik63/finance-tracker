from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.transaction import TransactionPublic, TransactionCreate, TransactionFilter, TransactionListResponse

router = APIRouter(prefix="/fin", tags=["finances, transactions"])


@router.post("/", response_model=TransactionPublic)
async def post_transaction(transaction: TransactionCreate, user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)) -> Transaction:
    db_trans = Transaction(value=transaction.value, date=transaction.date.timestamp(), category=transaction.category,
                           user_id=user.id)

    session.add(db_trans)
    await session.commit()
    await session.refresh(db_trans)

    return db_trans


def apply_filters(statement, filters: TransactionFilter, user_id):
    statement = statement.where(Transaction.user_id == user_id)
    conditions = []

    if filters.from_date and filters.to_date:
        conditions.append(Transaction.date >= int(
            datetime.combine(filters.from_date, datetime.min.time(), tzinfo=timezone.utc).timestamp()))
        conditions.append(Transaction.date < int(
            datetime.combine(filters.to_date, datetime.max.time(), tzinfo=timezone.utc).timestamp()))

    if filters.type:
        if filters.type == "expense":
            conditions.append(Transaction.value < 0)
        elif filters.type == "income":
            conditions.append(Transaction.value > 0)
    if filters.category:
        conditions.append(Transaction.category == filters.category)

    return statement.where(*conditions)


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session),

                           from_date: date | None = Query(None), to_date: date | None = Query(None),
                           type: Literal["expense", "income"] | None = Query(None), category: str | None = Query(None),
                           limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0, le=1000)):
    try:
        filters = TransactionFilter(
            from_date=from_date,
            to_date=to_date,
            type=type,
            category=category,
            limit=limit,
            offset=offset
        )

        statement = apply_filters(select(Transaction), filters, user.id)
        statement = statement.order_by(Transaction.date.asc())
        statement = statement.limit(filters.limit).offset(filters.offset)

        results = (await session.exec(statement)).all()

        return {"items": results, "count": len(results)}

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
