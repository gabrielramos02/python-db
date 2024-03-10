from fastapi import APIRouter, HTTPException, status, Depends
from middleware.check_auth import check_auth
from main import db_client
from odmantic import ObjectId
from db.models.imports import Paciente, User, Solicitud_Operacion, PacienteForm, Cama
from db.schemas.obtener_cama import obtener_cama
from datetime import datetime

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
    "/busqueda/{historia_clinica}",
)
async def eliminar(historia_clinica: str, user_auth: User = Depends(check_auth)):
    if user_auth.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente = await db_client.find_one(
        Paciente, Paciente.historia_clinica == historia_clinica
    )

    if paciente == None or not (paciente.enabled):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe paciente con esa historia clinica",
        )
    paciente.enabled = False
    await db_client.remove(
        Solicitud_Operacion, Solicitud_Operacion.paciente == paciente.id
    )
    cama = await db_client.find_one(Cama, Cama.paciente == paciente.id)
    cama.ocupada = False
    cama.paciente = None
    paciente.cama = cama

    paciente_db = await db_client.save(paciente)

    return paciente_db


@router.post("/")
async def add_paciente(paciente: PacienteForm, user_auth: User = Depends(check_auth)):
    if user_auth.role == "medico":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente_db = await db_client.find_one(
        Paciente, (Paciente.historia_clinica == paciente.historia_clinica)
    )
    cama = await obtener_cama(paciente.cama, paciente.sala)
    if paciente_db != None:
        if not (paciente_db.enabled):
            paciente_db.enabled = True
            cama.ocupada = True
            cama.paciente = paciente_db.id
            paciente_db.cama = cama
            await db_client.save(paciente_db)
            return paciente_db
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El paciente ya existe"
        )
    paciente_db = Paciente(
        name=paciente.name,
        surname=paciente.surname,
        historia_clinica=paciente.historia_clinica,
        cama=cama,
    )
    cama.ocupada = True
    cama.paciente = paciente_db.id
    await db_client.save(paciente_db)
    return paciente_db


@router.get("/busqueda/{historia_clinica}")
async def get_paciente(historia_clinica: str, user_auth: User = Depends(check_auth)):
    if user_auth.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente_db = await db_client.find_one(
        Paciente,
        (Paciente.historia_clinica == historia_clinica) & (Paciente.enabled == True),
    )
    if paciente_db != None and paciente_db.enabled:
        return paciente_db
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No existe ningun paciente con esa historia clinica",
    )


@router.get("/")
async def get_pacientes_por_fecha(
    fecha_inicio: str, fecha_fin: str, user: User = Depends(check_auth)
):
    if user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    pacientes = await db_client.find(
        Paciente,
        (Paciente.fecha_ingreso > fecha_inicio) & (Paciente.fecha_ingreso < fecha_fin),
    )
    if pacientes.__len__() == 0:
        return {"msg": "No hay pacientes"}
    return pacientes

