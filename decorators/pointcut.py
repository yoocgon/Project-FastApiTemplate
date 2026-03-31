
import functools

from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session

from core.oracle import get_session as get_oracle
from core.sqlite import get_session as get_sqlite
from models.token import Token
from models.user import User
from repositories.token import TokenRepository
from utils.auth import decode_jwt


def role(**params):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            #
            access_token = ''
            #
            if 'request' in params:               
                request: Request = kwargs['request']
            #
            if 'jwt' in params:
                payload_name = kwargs['jwt']
                #
                if payload_name in kwargs:
                    payload = kwargs[payload_name] 
                    access_token = payload['access_token']
            #
            if 'token' in kwargs:               
                token: Token = kwargs['token']
                access_token = token.access_token
            #
            jwt_dict = decode_jwt(access_token)
            user_id = jwt_dict.get("sub")
            # 사용자 롤 검사
            oracle_session: Session = get_oracle()
            sqlite_session: Session = get_sqlite()
            token_repo = TokenRepository(oracle=oracle_session, sqlite=sqlite_session)
            data = token_repo.read_token_user(user_id, token.access_token)
            if params['role'] == data['group']:
                result = func(*args, **kwargs)
            #
            return result
        return wrapper
    return decorator


