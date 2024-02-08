from fastapi import FastAPI, HTTPException, status
from db.models.user import User
from db.client import db_client, ObjectId
from routers import login
from passlib.context import CryptContext

app = FastAPI()
app.include_router(login.router)
crypth = CryptContext(schemes=["bcrypt"])


@app.post("/")
async def user(user: User):
    user.password = crypth.encrypt(user.password)
    await db_client.save(user)
    return user


@app.get("/")
async def user(id: ObjectId):
    result = await db_client.find_one(User, User.id == id)
    if result == None:
        raise HTTPException(status_code=404)
    result = password_free(result)
    return result


@app.get("/all")
async def users():
    users = await db_client.find(User)
   
    return users  


@app.put("/")
async def user(id: ObjectId):
    print(id)
    user = await db_client.find_one(User, (User.id == id) & (User.enabled == True))
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    user.enabled = False
    print(user.enabled)
    await db_client.save(user)
    raise HTTPException(status_code=status.HTTP_202_ACCEPTED)


def password_free(user: User) -> User:
    user.password = " "
    return user