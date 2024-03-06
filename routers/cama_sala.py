from fastapi import APIRouter, Depends, HTTPException, status
from main import db_client
from db.models.imports import Cama, Sala, User
from middleware.check_auth import check_auth


router = APIRouter(prefix="/disponibilidad", tags=["camas y salas"])


@router.get("/")
async def disponibilidad(user: User = Depends(check_auth)):
    if user.role == "medico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    camas = await db_client.find(Cama)
    return camas