import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user import User
from app.routers.auth import hash_password
from app.schemas.user import UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)) -> User:
    db_user = (await session.exec(select(User).where(User.username == user.username))).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hash_password=hashed_password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

@router.post("/login")
async def login(user: UserCreate, session: AsyncSession = Depends(get_session)):
    db_user = (await session.exec(select(User).where(User.username == user.username))).first()
    is_password = bcrypt.checkpw(user.password.encode("utf-8"), db_user.hash_password)

    if is_password:
        return {"answer": "Right password!"}
    else:
        raise HTTPException(400, "Incorrect password!")
