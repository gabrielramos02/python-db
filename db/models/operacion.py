from typing import Optional
from odmantic import Model, Reference, Field
from datetime import datetime, time
from db.models.imports import User, Paciente


class Operacion(Model):
    clasificacion: str
    fecha_solicitud: datetime = datetime.now()
    tiempo_duracion_estimado: str


class Solicitud_Operacion(Model):
    clasificacion: str
    fecha_solicitud: datetime = datetime.now()
    tiempo_duracion_estimado: str
    encargado: User = Reference(key_name="id_encargado")
    paciente: Paciente = Reference(key_name="id_paciente")


class Operacion_Realizada(Model):
    clasificacion: str
    fecha_solicitud: datetime = datetime.now()
    fecha_realizada: datetime = datetime.now()
    tiempo_duracion_estimado: str
    encargado: User = Reference(key_name="id_encargado")
    paciente: Paciente = Reference(key_name="id_paciente")
    tiempo_duracion_real: str
    descripcion: str


class Operacion_Planificada(Model):
    hora_ejecucion: str
    solicitud_operacion: Solicitud_Operacion = Reference(
        key_name="id_solicitud_operacion"
    )
