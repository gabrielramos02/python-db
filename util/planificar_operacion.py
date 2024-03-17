
from fastapi_utilities import repeat_at
from db.models.imports import Operacion_Planificada,Solicitud_Operacion
from main import db_client
from datetime import datetime,timedelta


@repeat_at(cron="* 1 * * *")
async def llamar_planificacion():
    await planificar_operacion()


async def planificar_operacion():
    operaciones_db = await db_client.find_one(Operacion_Planificada)
    
    if operaciones_db != None:
        await db_client.remove(Operacion_Planificada)

    prioritarias = await db_client.find(
        Solicitud_Operacion,
        Solicitud_Operacion.clasificacion == "prioritaria",
        sort=Solicitud_Operacion.fecha_solicitud,
    )
    regulares = await db_client.find(
        Solicitud_Operacion,
        Solicitud_Operacion.clasificacion == "regular",
        sort=Solicitud_Operacion.fecha_solicitud,
    )
    hora_actual = "08:00"
    for operacion in prioritarias:
        hora_actual_datetime = datetime.strptime(hora_actual, "%H:%M")

        estimado_datetime = datetime.strptime(
            operacion.tiempo_duracion_estimado, "%H:%M"
        )

        if (hora_actual_datetime.hour + estimado_datetime.hour) < 25:
            operacion_planificada = Operacion_Planificada(
                solicitud_operacion=operacion, hora_ejecucion=hora_actual
            )
            await db_client.save(operacion_planificada)

            hora_actual_datetime = hora_actual_datetime + timedelta(
                hours=estimado_datetime.hour, minutes=estimado_datetime.minute
            )
            hora_actual = datetime.strftime(hora_actual_datetime, "%H:%M")

    for index, operacion in enumerate(regulares):
        hora_actual_datetime = datetime.strptime(hora_actual, "%H:%M")
        
        estimado_datetime = datetime.strptime(
            operacion.tiempo_duracion_estimado, "%H:%M"
        )
        if hora_actual_datetime.hour < 14:
            hora_actual_datetime = hora_actual_datetime.replace(hour=14)

        if (hora_actual_datetime.hour + estimado_datetime.hour) < 25:
            hora_actual = datetime.strftime(hora_actual_datetime, "%H:%M")
            operacion_planificada = Operacion_Planificada(
                solicitud_operacion=operacion, hora_ejecucion=hora_actual
            )

            hora_actual_datetime = hora_actual_datetime + timedelta(
                hours=estimado_datetime.hour, minutes=estimado_datetime.minute
            )

            hora_actual = datetime.strftime(hora_actual_datetime, "%H:%M")
            await db_client.save(operacion_planificada)

        if index > 5:
            break

    return
