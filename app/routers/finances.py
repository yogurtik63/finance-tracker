from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.transaction import TransactionPublic, TransactionCreate

router = APIRouter(prefix="/fin", tags=["finances, transactions"])

@router.post("/", response_model=TransactionPublic)
async def post_transaction(transaction: TransactionCreate, user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)):
    db_trans = Transaction(value=transaction.value, date=transaction.date, user_id=user.id)

    session.add(db_trans)
    await session.commit()
    await session.refresh(db_trans)

    return db_trans
