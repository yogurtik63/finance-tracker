from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user import User
from app.routers.auth import hash_password, create_access_token, create_refresh_token, verify_password, decode_token
from app.schemas.user import UserCreate, UserPublic, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


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
async def login(response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(User).where(User.username == user.username))
    db_user = result.first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    is_password = verify_password(user.password, db_user.hash_password)

    if is_password:
        access_token = create_access_token({"sub": str(db_user.id)})
        refresh_token = create_refresh_token({"sub": str(db_user.id)})

        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return {"answer": "Correct password!"}
    else:
        raise HTTPException(400, detail="Incorrect password!")


@router.get("/credentials", response_model=UserPublic)
async def get_credentials(session: AsyncSession = Depends(get_session),
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = decode_token(credentials.credentials)

    user_id = token.get("sub")

    if not user_id:
        raise HTTPException(401, detail="User id not found")

    result = await session.exec(select(User).where(User.id == int(user_id)))

    if not result:
        raise HTTPException(401, detail="User not found")

    return result.first()


@router.post("/refresh")
async def refresh_token(response: Response, refresh_token: str | None = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(401, detail="No refresh token")

    token = decode_token(refresh_token)
    user_id = token.get("sub")

    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"answer": "Token refreshed successfully!"}
