from fastapi import APIRouter, Depends, HTTPException, status
from main import db_client
from db.models.imports import Cama, Sala, User
from middleware.check_auth import check_auth


router = APIRouter(tags=["camas y salas"])


@router.get("/disponibilidad")
async def disponibilidad(user: User = Depends(check_auth)):
    if user.role == "medico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    camas = await db_client.find(Cama)
    return camas


@router.get("/ocupacion")
async def ocupacion(user: User = Depends(check_auth)):
    if user.role == "medico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    salas = await db_client.find(Sala, Sala.numero != "vacia")
    ocupacion = []
    for sala in salas:
        ocupadas = await db_client.count(
            Cama, (Cama.ocupada == True) & (Cama.sala == sala.id)
        )
        info_sala = {"sala": sala.numero, "ocupacion": ocupadas}
        ocupacion.append(info_sala)

    return ocupacion
