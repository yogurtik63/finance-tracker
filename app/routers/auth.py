from dotenv import load_dotenv
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import *
from app.core.security import pwd_context, security
from app.database import get_session
from app.models.user import User

load_dotenv()

from datetime import datetime, timedelta

from pydantic import BaseModel
from fastapi import HTTPException, Depends

import jwt


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=12)  # minutes=30
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=3)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt

def decode_token(str_token: str):
    try:
        return jwt.decode(str_token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except BaseException as e:
        raise e

async def get_current_user(session: AsyncSession = Depends(get_session),
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = decode_token(credentials.credentials)

    user_id = token.get("sub")

    if not user_id:
        raise HTTPException(401, detail="User id not found")

    result = await session.exec(select(User).where(User.id == int(user_id)))

    if not result:
        raise HTTPException(401, detail="User not found")

    return result.first()
