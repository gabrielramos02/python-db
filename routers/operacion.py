from fastapi import APIRouter, HTTPException, status, Depends
from main import db_client, User
from middleware.check_auth import check_auth
from db.models.operacion import Operacion, Solicitud_Operacion, Operacion_Realizada
from db.models.paciente import Paciente
from odmantic import ObjectId, Model
from db.schemas.password_free_models import password_free

router = APIRouter(prefix="/operacion", tags=["operacion"])


@router.get("/all")
async def all_operaciones(user: User = Depends(check_auth)):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    operaciones = await db_client.find(Solicitud_Operacion)
    if operaciones.__len__() == 0:
        return {"msg": "No hay operaciones"}
    return operaciones


@router.post("/addoperacion/{id_paciente}")
async def add_operacion(
    operacion: Operacion, id_paciente: str, user: User = Depends(check_auth)
):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente = await db_client.find_one(Paciente,Paciente.id ==ObjectId(id_paciente))
    operacion_db = await db_client.find_one(
        Solicitud_Operacion,
        Solicitud_Operacion.paciente==paciente.id,
    )
    
    if operacion_db != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La operacion ya existe"
        )
    paciente = await db_client.find_one(Paciente, Paciente.id == ObjectId(id_paciente))

    solicitud_operacion = Solicitud_Operacion(
        encargado=user,
        paciente=paciente,
        clasificacion=operacion.clasificacion,
        fecha_solicitud=operacion.fecha_solicitud,
        tiempo_duracion_estimado=operacion.tiempo_duracion_estimado,
    )
    await db_client.save(solicitud_operacion)
    return solicitud_operacion


@router.get("/me")
async def user_operaciones(user: User = Depends(check_auth)):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    operaciones = await db_client.find(Solicitud_Operacion)
    operaciones_user = []
    for operacion in operaciones:

        user_new = password_free(operacion.encargado)
        if user_new == user:
            operaciones_user.append(operacion)
    return operaciones_user


# TODO: fix parametros
@router.post("/operacionrealizada/{id_operacion}")
async def operacionDone(
    id_operacion: str,
    tiempo_real: str,
    descripcion: str,
    user: User = Depends(check_auth),
):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )

    solicitud_operacion_db = await db_client.find_one(
        Solicitud_Operacion, Solicitud_Operacion.id == ObjectId(id_operacion)
    )
    if solicitud_operacion_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="La soliciud no existe"
        )

    operacion_realizada_db = Operacion_Realizada(
        id=solicitud_operacion_db.id,
        clasificacion=solicitud_operacion_db.clasificacion,
        fecha_solicitud=solicitud_operacion_db.fecha_solicitud,
        tiempo_duracion_estimado=solicitud_operacion_db.tiempo_duracion_estimado,
        encargado=solicitud_operacion_db.encargado,
        paciente=solicitud_operacion_db.paciente,
        tiempo_duracion_real=tiempo_real,
        descripcion=descripcion,
    )
    await db_client.remove(solicitud_operacion_db)
    await db_client.save(operacion_realizada_db)
    return operacion_realizada_db


@router.get("/busqueda/{id_paciente}")
async def get_operacion(idpaciente: str, user: User = Depends(check_auth)):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    operacion_db = await db_client.find_one(
        Solicitud_Operacion, Solicitud_Operacion.id == ObjectId(idpaciente)
    )


@router.post("/urgencia")
async def operacion_urgencia(
    operacion: Operacion, paciente_form: Paciente, user: User = Depends(check_auth)
):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )

    paciente = await db_client.find_one(
        Paciente,
        (Paciente.name == paciente_form.name)
        & (Paciente.surname == paciente_form.surname),
    )

    if paciente != None:
        if not (paciente.enabled):
            paciente.enabled == True
            await db_client.save(paciente)
    else:
        paciente = Paciente(
            name=paciente_form.name, surname=paciente_form.surname
        )
        await db_client.save(paciente)

    operacion_urgente = Solicitud_Operacion(
        clasificacion=operacion.clasificacion,
        fecha_solicitud=operacion.fecha_solicitud,
        tiempo_duracion_estimado=operacion.tiempo_duracion_estimado,
        encargado=user,
        paciente=paciente,
    )
    await db_client.save(operacion_urgente)
    return operacion_urgente
