

from datetime import datetime, timedelta, timezone
from fastapi import status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from jose import jwt, jws

import core.auth as auth
import core.setting as setting

from core.auth import keys, get_recommand_kid


def get_password_hash(password):
    return auth.password_hash.hash(password)


def verify_password(plain_password, password):
    return auth.password_hash.verify(plain_password, password)


def encode_jwt(data: dict, user_id: str):
    #
    settings = setting.settings
    #
    data["sub"] = user_id
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    #
    kid, secret_key = get_recommand_kid()
    #
    encoded_jwt = jwt.encode(
        data, 
        secret_key, 
        algorithm=settings.ALGORITHM,
        headers={"kid": kid}
    )
    #
    return encoded_jwt


def decode_jwt(token: str) -> dict:
    #
    settings = setting.settings
    #
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    #
    try:
        #
        kid = jwt.get_unverified_header(token).get("kid")
        #
        if kid not in auth.keys:
            raise credentials_exception
        #
        # 토근 만기 여부 검사 작성 필요
        # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        #
        secret_key = auth.keys[kid]
        # 토큰 유효성 검사
        jwt_dict = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        # 사용자 아이디 존재 여부 검사
        user_id = jwt_dict.get("sub")
        if user_id is None:
            raise credentials_exception
        #
        return jwt_dict
    #
    except InvalidTokenError:
        raise credentials_exception
    #    
    return None


def refresh_token(payload) -> dict:
    #
    jwt_dict = decode_jwt(payload)
    encode_jwt(jwt_dict, jwt_dict["sub"])

