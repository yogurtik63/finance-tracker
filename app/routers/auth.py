import os

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
    # return bcrypt.hashpw(password.encode("utf-8"), salt=salt).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
    # return bcrypt.checkpw(check_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token() -> str:
    return ""

def decode_token():
    return
