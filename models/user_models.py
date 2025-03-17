from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str = Field(default=None, nullable=False)
    first_name: str = Field(default=None, nullable=False)
    last_name: str = Field(default=None, nullable=False)
    superuser: bool = Field(default=False, nullable=False)


class User(UserBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)
    password_hash: str = Field(default=None, nullable=False)
