from fastapi import APIRouter, HTTPException, Depends, status, Request
from main import db_client
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from db.models.imports import User


ALGORITHM = "HS256"
ACCESS_TOKE_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"


router = APIRouter(prefix="/login", tags=["login"])
crypth = CryptContext(schemes=["bcrypt"])


@router.post("")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_login = await db_client.find_one(User, User.username == form.username)
    if user_login == None:  # Verifica si el usuario existe
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    if not (user_login.enabled):  # Verifica si el usuario es habilitado
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario desactivado "
        )
    if not crypth.verify(form.password, user_login.password):  # Verifica la constrase;a
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrase;a incorrecta"
        )

    # Creando el jwt token
    access_token = {
        "sub": user_login.id.__str__(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKE_DURATION),
    }

    return {
        "access_token": jwt.encode(access_token, key=SECRET, algorithm=ALGORITHM),
        "access_type": "bearer",
    }
