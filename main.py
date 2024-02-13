from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.models.user import User
from db.client import db_client
from routers import login, user, paciente, operacion
from passlib.context import CryptContext

ALGORITHM = "HS256"
ACCESS_TOKE_DURATION = 30
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"
crypth = CryptContext(schemes=["bcrypt"])

app = FastAPI(root_path="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(user.router)
app.include_router(paciente.router)
app.include_router(operacion.router)
