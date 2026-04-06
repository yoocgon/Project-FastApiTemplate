
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel
from typing import Optional

from core.oracle import get_metadata


class UserORM(SQLModel, table=True, metadata=get_metadata()):
    __tablename__: str = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    password: str = Field()
    email: str = Field()
    group: str = Field(default='user')
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    user_id: str
    password: str
    email: str
    group: str

