from typing import Annotated
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer,SecurityScopes
from main import db_client
from jose import jwt, JWTError
from odmantic import ObjectId
from db.schemas.password_free_models import password_free, password_free_all
from db.models.imports import User

ALGORITHM = "HS256"
ACCESS_TOKE_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

async def check_auth(token: str = Depends(oauth2)):
    try:
        decoded = jwt.decode(token=token, key=SECRET, algorithms=ALGORITHM)
        if decoded.get("sub") == None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await db_client.find_one(User, User.id == ObjectId(decoded.get("sub")))

    if user.enabled:
        return password_free(user)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario Inactivo"
    )
