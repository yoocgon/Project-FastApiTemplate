
from fastapi import HTTPException, status, Depends

from models.user import User
from repositories.user import UserRepository


class UserService:


    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo


    def create_user(self, user: User):
        #
        user = self.user_repo.create(user)
        return user


    def read_user(self, id: int):
        #
        users = self.user_repo.read_id(id)
        return users


    def read_user_id(self, id: int):
        #
        users = self.user_repo.read_user_id(id)
        return users


    def read_users(self, offset: int, limit: int):
        #
        users = self.user_repo.read_ragne(offset, limit)
        return users


    def update_user(self, id: int, user: User):
        #
        user = self.user_repo.update(id, user)
        return user
    


    def delete_user(self, id: int):
        #
        user = self.user_repo.delete(id)
        #
        if user:
             result = "ok"
        else:
             result = "There's no matched Hero"
        #
        return {
            "result": result, 
            "hero": user
        }
