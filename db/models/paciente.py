from odmantic import Model, Reference
from datetime import datetime
from typing import Optional
from db.models.cama_sala import Cama


class Paciente(Model):
    name: str
    surname: str
    fecha_ingreso: datetime = datetime.now()
    historia_clinica: Optional[str] = None
    cama: Cama = Reference(key_name="id_cama")
    enabled: bool = True


class PacienteForm(Model):
    name: str
    surname: str
    historia_clinica: Optional[str] = None
    cama: Optional[str] = None
    sala: Optional[str] = None
