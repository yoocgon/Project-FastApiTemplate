
import json
import pandas as pd
import sqlparse
import sys

from datetime import timedelta
from fastapi import HTTPException, status, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlmodel import Session
from typing import List

from core.oracle import get_db, get_sql
from models.hero import HeroORM, Hero


class HeroRepository:

    #
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db


    def create(self, hero: Hero) -> Hero:
        #
        model = HeroORM.model_validate(hero)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model


    # def read_id(self, id: int):
    #     #
    #     db = self.db.get(Hero, id)
    #     return db


    def read_id(self, id: str) -> Hero:
        #
        query = get_sql('hero', 'insert', {"id": id})
        df = pd.read_sql(query, self.db.bind)
        dicts = df.to_dict(orient="records")
        if len(dicts) != 1:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found")
        #       
        hero = Hero(**dicts[0])
        return hero


    def read_ragne(self, offset: int, limit: int) -> List[Hero]:
        #
        statement = select(HeroORM).offset(offset).limit(limit)
        models: List[Hero] = self.db.exec(statement).scalars().all()
        return models


    def update(self, id: int, hero: Hero) -> Hero:
        #
        model = self.db.get(HeroORM, id)
        if not model:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hero not found")
        hero_data = hero.model_dump(exclude_unset=True)
        model.sqlmodel_update(hero_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model


    def delete(self, id: int) -> Hero:
        #
        model = self.db.get(HeroORM, id)
        if not model:
            return None
        #
        self.db.delete(model)
        self.db.commit()
        return model
