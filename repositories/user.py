
import json
import pandas as pd
import sqlparse
import sys

from datetime import timedelta
from fastapi import HTTPException, status, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlmodel import Session
from typing import Annotated, List

from core.oracle import get_db, get_sql
from core.logger import log_df
from models.user import UserORM, User
from utils.auth import get_password_hash


class UserRepository:

    #
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db


    def create(self, user: User) -> User:
        #
        model = UserORM.model_validate(user)
        model.password = get_password_hash(model.password)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model


    def create2(self, user: User) -> User:
        #
        model = UserORM.model_validate(user)
        user_id = model.user_id
        email = model.email
        group = model.group
        hashed_password = get_password_hash(model.password)
        #
        query = get_sql('user', 'insert')
        #
        # query = f"""
        
        #     INSERT INTO user ( 
        #         user_id, 
        #         password, 
        #         email, 
        #         "group"
        #     ) VALUES (
        #         '{user_id}', 
        #         '{hashed_password}', 
        #         '{email}', 
        #         '{group}'
        #     )

        # """
        #
        self.db.exec(text(query))
        self.db.commit()
        self.db.refresh(user)
        #
        return user


    def read_id(self, id: int) -> User:
        #
        model = self.db.get(UserORM, id)
        return model
    

    def read_user_id(self, user_id: str) -> User:
        #
        query = f"""

            SELECT 
                * 
            FROM 
                user 
            WHERE 
                user_id='{user_id}' 
                
        """
        #
        df = pd.read_sql(query, self.db.bind)
        log_df(df, level='INFO')
        if len(df) != 1:
            raise Exception(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="User not found")
        #       
        # users_dict = df.to_dict(orient="records")
        # user = User(**user_dict)
        user_dict = df.iloc[0].to_dict()
        user_id = user_dict.get('user_id')
        password = user_dict.get('password')
        email = user_dict.get('email')
        group = user_dict.get('group')
        user = UserORM(user_id=user_id, password=password, email=email, group=group)
        return user
    

    def read_ragne(self, offset: int, limit: int) -> List[User]:
        #
        statement = select(UserORM).offset(offset).limit(limit)
        models: List[User] = self.db.exec(statement).scalars().all()
        return models


    def update(self, id: int, user: User) -> User:
        #
        model = self.db.get(UserORM, id)
        if model:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        model.sqlmodel_update(user_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model


    def delete(self, id: int) -> User:
        #
        model = self.db.get(UserORM, id)
        if not model:
            return None
        #
        self.db.delete(model)
        self.db.commit()
        return model
