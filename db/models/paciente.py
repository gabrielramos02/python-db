from odmantic import Model
from datetime import date
from typing import Optional

class Paciente(Model):
    name: str
    surname: str
    fecha_ingreso: str = str(date.today())
    historia_clinica: Optional[str] = None
    cama: Optional[str] = None
    sala: Optional[str] = None
    enabled: bool = True

