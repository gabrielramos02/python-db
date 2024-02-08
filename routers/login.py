from fastapi import APIRouter,HTTPException,Depends,status
from main import User,db_client
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt,JWTError

ALGORITHM = "HS256"
ACCESS_TOKE_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"
crypth = CryptContext(schemes=["bcrypt"])
router = APIRouter(prefix="/login",tags=["login"])

@router.post("/")
async def login(form:OAuth2PasswordRequestForm = Depends()):
    user_login = await db_client.find_one(User, User.username == form.username)
    if user_login == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado")
    if not crypth.verify(form.password,user_login.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Contrase;a incorrecta")
    
    access_token = {
        "sub":user_login.username,
        "exp":datetime.utcnow()+timedelta(minutes=ACCESS_TOKE_DURATION)
    }

    return {"access_token":jwt.encode(access_token,key=SECRET,algorithm=ALGORITHM),"access_type":"bearer"}