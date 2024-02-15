from fastapi import APIRouter, HTTPException, status, Depends
from middleware.check_auth import check_auth
from main import db_client, User
from odmantic import ObjectId
from db.models.paciente import Paciente

router = APIRouter(prefix="/paciente", tags=["paciente"])


@router.get("/all")
async def all_pacientes(user: User = Depends(check_auth)):
    if user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    pacientes = await db_client.find(Paciente, Paciente.enabled == True)
    if pacientes.__len__() == 0:
        return {"msg": "No hay pacientes"}
    return pacientes


@router.put(
    "/{id}",
)
async def eliminar(id: str, user_auth: User = Depends(check_auth)):
    if user_auth.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente = await db_client.find_one(Paciente, Paciente.id == ObjectId(id))
    if paciente == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    paciente.enabled = False
    await db_client.save(paciente)
    return paciente


@router.post("/")
async def add_paciente(paciente: Paciente, user_auth: User = Depends(check_auth)):
    if user_auth.role == "medico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente_db = await db_client.find_one(
        Paciente,
        (Paciente.historia_clinica == paciente.historia_clinica)
        & (Paciente.enabled == True),
    )
    if paciente_db != None:
        if not (paciente_db.enabled):
            paciente_db.enabled == True
            await db_client.save(paciente_db)
            return paciente_db
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El paciente ya existe"
        )
    await db_client.save(paciente)
    return paciente


@router.get("/{historia_clinica}")
async def get_paciente(historia_clinica: str, user_auth: User = Depends(check_auth)):
    if user_auth.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente_db = await db_client.find_one(
        Paciente,
        (Paciente.historia_clinica == historia_clinica)
        & (Paciente.enabled == True),
    )
    if paciente_db != None:
        return paciente_db
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No existe ningun paciente con esa historia clinica"
        )
    
