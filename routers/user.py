
from fastapi import APIRouter, Request, Depends, Query
from typing import Annotated

from decorators.pointcut import role as role_check
from depends.role import role
from models.token import Token
from models.user import User
from services.user import UserService


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=list[User])
async def get_useres(
    service: UserService = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    #
    response = service.read_users(offset, limit)
    return response 


@router.get("/id={id}/user", response_model=User)
def get_user(id: int, service: UserService = Depends()):
    #
    response = service.read_user(id)
    return response


@router.get("/user_id={user_id}/user", response_model=User)
def get_user_2(user_id: str, service: UserService = Depends()):
    #
    response = service.read_user_id(user_id)
    return response


@router.post("/user/v1", response_model=User)
@role_check(role='admin')
def get_user_3(token: Token, user: User, request: Request, service: UserService = Depends()):
    #
    response = service.read_user_id(user.user_id)
    return response


@router.post("/user/v2", response_model=User)
def get_user_4(token: Annotated[Token, Depends(role('admin'))], user: User, service: UserService = Depends()):
    #
    response = service.read_user_id(user.user_id)
    return response


@router.post("/add", response_model=User)
def add_user(user: User, service: UserService = Depends()):
    #
    response = service.create_user(user)
    return response


@router.patch("/{id}", response_model=User)
def update_user(id: int, user: User, service: UserService = Depends()):
    #
    response = service.update_user(id, user)
    return response


@router.delete("/{id}")
def delete_user(id: int, service: UserService = Depends()):
    #
    response = service.delete_user(id)
    return response
