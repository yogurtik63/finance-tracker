from fastapi import APIRouter, Depends
from sqlmodel import select, extract
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.transaction import TransactionPublic, TransactionCreate, TransactionFilter

router = APIRouter(prefix="/fin", tags=["finances, transactions"])


@router.post("/", response_model=TransactionPublic)
async def post_transaction(transaction: TransactionCreate, user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)) -> Transaction:
    db_trans = Transaction(value=transaction.value, date=transaction.date, category=transaction.category,
                           user_id=user.id)

    session.add(db_trans)
    await session.commit()
    await session.refresh(db_trans)

    return db_trans


def apply_filters(statement, filters: TransactionFilter, user_id):
    statement = statement.where(Transaction.user_id == user_id)
    conditions = []
    
    if filters.year:
        conditions.append(extract("year", Transaction.date) == filters.year)
    if filters.month:
        conditions.append(extract("month", Transaction.date) == filters.month)
    if filters.day:
        conditions.append(extract("day", Transaction.date) == filters.day)

    if filters.type:
        if filters.type == "expense":
            conditions.append(Transaction.value < 0)
        elif filters.type == "income":
            conditions.append(Transaction.value > 0)
    if filters.category:
        conditions.append(Transaction.category == filters.category)

    return statement.where(*conditions)


@router.get("/")
async def get_transactions(user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session),
                           filters: TransactionFilter = Depends()):

    statement = apply_filters(select(Transaction), filters, user.id)
    statement = statement.order_by(Transaction.date.desc())
    statement = statement.limit(filters.limit).offset(filters.offset)

    results = (await session.exec(statement)).all()

    return {"items": results, "count": len(results)}
