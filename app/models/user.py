from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    username: str = Field(nullable=False, index=True, unique=True)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hash_password: str = Field(nullable=False)
