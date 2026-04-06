
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel
from typing import Optional

from core.sqlite import get_metadata


class TokenORM(SQLModel, table=True, metadata=get_metadata()):
    __tablename__: str = "token"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    access_token: str = Field(index=True)
    token_type: str = Field(default='bearer')
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    user_id: str
    access_token: str
    token_type : str = 'bearer'
