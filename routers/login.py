
from fastapi import APIRouter, status, HTTPException, Depends 

from models.token import Token
from models.user import User
from services.login import LoginService

#
router = APIRouter(prefix="/login", tags=["login"])

#
@router.post("/", response_model=Token)
async def login(user: User, service: LoginService = Depends()):
    #
    if(service.verify_passwrod(user)):
        token = service.isseue_token(user)
        return token
    #
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hero not found")

#
@router.post("/signup")
async def post_signup(user: User, service: LoginService = Depends()):
    #
    created_user: User = await service.create(user)
    return created_user

# signout
