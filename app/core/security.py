from fastapi.security import HTTPBearer
from passlib.context import CryptContext

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"])
