
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

from core.oracle import get_db as get_oracle
from core.sqlite import get_db as get_sqlite
from models.token import TokenORM, Token
from models.user import User


class TokenRepository:

    #
    def __init__(self, sqlite: Session = Depends(get_sqlite), oracle: Session = Depends(get_oracle)):
        self.sqlite = sqlite
        self.oracle = oracle


    def create(self, token: Token) -> Token:
        #
        model = TokenORM.model_validate(token)
        self.sqlite.merge(model)
        self.sqlite.commit()
        #
        model = self.sqlite.scalars(select(TokenORM)\
            .where(TokenORM.user_id == model.user_id)\
                .where(TokenORM.access_token == model.access_token)).first()
        #
        return model


    def read_user_id(self, user_id: str) -> Token:
        #
        query = f"""

            SELECT 
                * 
            FROM 
                token 
            WHERE 
                user_id='{user_id}' 
                
        """
        #
        df = pd.read_sql(query, self.sqlite.bind)
        dicts = df.to_dict(orient="records")
        if len(dicts) != 1:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found")
        #       
        tonen = Token(**dicts[0])
        return tonen


    # def read_token_user(self, user_id: str, access_token: str):
    #     #
    #     query = f"""

    #         SELECT	u.user_id, u."group", t.access_token, t.token_type
    #         FROM token t
    #         JOIN user u ON t.user_id = u.user_id AND t.user_id = '{user_id}'
    #         WHERE t.access_token = '{access_token}'
                
    #     """
    #     #
    #     df = pd.read_sql(query, self.db.bind)
    #     dicts = df.to_dict(orient="records")
    #     if len(dicts) == 0:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token not found")
    #     #       
    #     user = Token(**dicts[0])
    #     return user


    def read_token_user(self, user_id: str, access_token: str) -> dict:
        #
        query = f"""
            SELECT	t.user_id, t.access_token, t.token_type
            FROM token t
            WHERE t.user_id = '{user_id}' 
                AND t.access_token = '{access_token}'
        """
        #
        df_token = pd.read_sql(query, self.sqlite.bind)
        token_dicts = df_token.to_dict(orient="records")
        #
        query = f"""
            SELECT	u.user_id, u."group"
            FROM user u
            WHERE u.user_id = '{user_id}' 
        """
        #
        df_user = pd.read_sql(query, self.oracle.bind)
        user_dicts = df_user.to_dict(orient="records")
        #
        if len(df_user) == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token not found")
        # 
        # token = Token(**dicts[0])
        #
        user_id = user_dicts[0]['user_id']
        group = user_dicts[0]['group']
        #
        return {"user_id": user_id, "group": group}
