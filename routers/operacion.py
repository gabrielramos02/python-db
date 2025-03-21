from fastapi import APIRouter, HTTPException, status, Depends
from main import db_client
from middleware.check_auth import check_auth
from odmantic import ObjectId, Model
from db.schemas.password_free_models import password_free
from datetime import datetime, timedelta
from db.models.imports import (
    User,
    Operacion,
    Operacion_Realizada,
    Solicitud_Operacion,
    Paciente,
    PacienteForm,
    Cama,
    Operacion_Planificada,
)
from fastapi_utilities import repeat_at, repeat_every

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


@router.post("/addoperacion/{id_paciente}")
async def add_operacion(
    operacion: Operacion, id_paciente: str, user: User = Depends(check_auth)
):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    paciente = await db_client.find_one(Paciente, Paciente.id == ObjectId(id_paciente))
    operacion_db = await db_client.find_one(
        Solicitud_Operacion,
        Solicitud_Operacion.paciente == paciente.id,
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
    planificacion = await db_client.find_one(
        Operacion_Planificada,
        Operacion_Planificada.solicitud_operacion == solicitud_operacion_db.id,
    )
    if solicitud_operacion_db == None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="La solicitud no existe"
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
    await db_client.delete(solicitud_operacion_db)
    if planificacion != None:
        await db_client.remove(planificacion)
    await db_client.save(operacion_realizada_db)
    return operacion_realizada_db


@router.post("/urgencia", tags=["urgencias"])
async def operacion_urgencia(
    operacion: Operacion, paciente_form: PacienteForm, user: User = Depends(check_auth)
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
    cama_vacia = await db_client.find_one(Cama, Cama.numero == "vacia")

    if paciente != None:
        if not (paciente.enabled):
            paciente.enabled == True
            await db_client.save(paciente)
    else:
        paciente = Paciente(
            name=paciente_form.name, surname=paciente_form.surname, cama=cama_vacia
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


@router.get("/operacionesrealizadas")
async def operaciones_realizadas(
    fecha_inicio: str, fecha_fin: str, user: User = Depends(check_auth)
):
    if user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    operaciones_list = await db_client.find(
        Operacion_Realizada,
        (Operacion_Realizada.fecha_realizada > fecha_inicio)
        & (Operacion_Realizada.fecha_realizada < fecha_fin),
    )

    return operaciones_list


@router.get("/operacionesultimomes", tags=["urgencias"])
async def operaciones_ultimo_mes(user: User = Depends(check_auth)):
    if user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    fecha_mes_anterior = datetime.today()

    fecha_mes_anterior = fecha_mes_anterior.replace(day=(fecha_mes_anterior.month - 1))

    operaciones_urgencia = await db_client.find(
        Operacion_Realizada,
        (Operacion_Realizada.clasificacion == "urgencia")
        & (Operacion_Realizada.fecha_realizada > fecha_mes_anterior),
    )
    return operaciones_urgencia


@router.get("/operacionesplanificadas/all", tags=["planificadas"])
async def operaciones_planificadas_all(user: User = Depends(check_auth)):
    if user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    operaciones = await db_client.find(Operacion_Planificada)
    return operaciones


@router.get("/operacionesplanificadas/", tags=["planificadas"])
async def operaciones_planificadas(user: User = Depends(check_auth)):
    if user.role == "recepcionista":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no Autorizado"
        )
    solicitudes = await db_client.find(
        Solicitud_Operacion, Solicitud_Operacion.encargado == user.id
    )
    operaciones = await db_client.find(Operacion_Planificada)
    operaciones_me = []
    for solicitud in solicitudes:
        for operacion in operaciones:
            if operacion.solicitud_operacion == solicitud:
                operaciones_me.append(operacion)

    return operaciones_me
