
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import declarative_base
from sqlmodel import Field, SQLModel
from typing import Optional

from core.oracle import get_metadata


class HeroORM(SQLModel, table=True, metadata=get_metadata()):
    __tablename__: str = "hero"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None)
    secret_name: str = Field()
    model_config = ConfigDict(from_attributes=True)


class Hero(BaseModel):
    name: str
    age: int
    secret_name: str
