from fastapi import Depends,HTTPException,status
from middleware.check_auth import check_auth
from main import User

async def validate_authorization(user: User = Depends(check_auth)):
    return user.role