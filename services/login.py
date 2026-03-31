
from fastapi import status, HTTPException, Depends 

from models.token import Token
from models.user import User
from repositories.user import UserRepository
from repositories.token import TokenRepository
from utils.auth import encode_jwt, verify_password


class LoginService:


    def __init__(self, user_repo: UserRepository = Depends(), token_repo: TokenRepository = Depends()):
        self.user_repo = user_repo
        self.token_repo = token_repo


    # 사용자 추가
    async def create(self, user: User):
        #        
        user = self.user_repo.create(user)
        # user = self.user_repo.create2(user)
        if user == None:
            raise Exception
        # 
        return user
    

    # 평문 패스워드를 입력해서 해시패스워드랑 맞는지 확인
    def verify_passwrod(self, user :User):
        #
        model = self.user_repo.read_user_id(user.user_id)
        if not model:
            return None
        #
        if not verify_password(user.password, model.password):
            return None
        #
        if not model:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect user_id or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        #
        return True


    #
    def isseue_token(self, user: User):
        #
        access_token = encode_jwt({}, user.user_id)
        token = Token(user_id=user.user_id, access_token=access_token) 
        isseued_token = self.token_repo.create(token)
        return Token(access_token=access_token, user_id=isseued_token.user_id, token_type="bearer")
    
    