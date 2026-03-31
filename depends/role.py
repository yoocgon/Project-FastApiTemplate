
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Any

from core.oracle import get_session as get_oracle
from core.sqlite import get_session as get_sqlite
from models.token import Token
from models.user import User
from repositories.token import TokenRepository
from utils.auth import decode_jwt


# 실사용시
# def role(role: str):
#     async def _role_checker(payload: Any):
#         #
#         access_token = ''
#         #
#         if 'access_token' in payload:
#             access_token = payload.access_token
#         # 토큰 유효성 검사
#         jwt_dict = decode_jwt(access_token)
#         user_id = jwt_dict.get("sub")
#         # 사용자 롤 검사
#         oracle_session: Session = get_oracle()
#         sqlite_session: Session = get_sqlite()
#         token_repo = TokenRepository(oracle=oracle_session, sqlite=sqlite_session)
#         data = token_repo.read_token_user(user_id, access_token)
#         if data['group'] != role:
#             raise HTTPException(status_code=403, detail="Not enough permissions")
#         #
#         return True
#     return _role_checker


# Swagger 사용시
def role(role: str):
    async def _role_checker(payload: Token):
        #
        access_token = ''
        #
        if payload.access_token:
            access_token = payload.access_token
        # 토큰 유효성 검사
        jwt_dict = decode_jwt(access_token)
        user_id = jwt_dict.get("sub")
        # 사용자 롤 검사
        oracle_session: Session = get_oracle()
        sqlite_session: Session = get_sqlite()
        token_repo = TokenRepository(oracle=oracle_session, sqlite=sqlite_session)
        data = token_repo.read_token_user(user_id, access_token)
        if data['group'] != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        #
        return True
    return _role_checker

