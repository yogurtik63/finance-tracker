from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
