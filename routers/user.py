from fastapi import APIRouter, HTTPException, status, Depends
from odmantic import ObjectId
from main import db_client, User
from passlib.context import CryptContext
from middleware.check_auth import check_auth
from db.schemas.password_free_models import password_free, password_free_all


router = APIRouter(prefix="/user", tags=["user"])
crypth = CryptContext(schemes=["bcrypt"])


@router.post("/")
async def add_user(user: User, user_auth: User = Depends(check_auth)):
    if user_auth.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    userdb = await db_client.find_one(User, User.username == user.username)
    if userdb != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
        )
    user.password = crypth.encrypt(user.password)
    await db_client.save(user)
    return password_free(user)

@router.get("/all")
async def all_users(user: User = Depends(check_auth)):
    if user.role != "director":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Usuario no autorizado")
    users = await db_client.find(User, User.enabled == True)
    password_free_all(users)
    return users


@router.put("/{id}")
async def desactivar_user(id: str,user: User = Depends(check_auth)):
    user = await db_client.find_one(User, (User.id == ObjectId(id)) & (User.enabled == True))
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    user.enabled = False   
    await db_client.save(user)
    raise HTTPException(status_code=status.HTTP_202_ACCEPTED)

@router.get("/me")
async def user(user: User = Depends(check_auth)):
    return user