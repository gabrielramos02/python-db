from odmantic import Model
from datetime import datetime
from typing import Optional

class Paciente(Model):
    name: str
    surname: str
    fecha_ingreso: datetime = datetime.now()
    historia_clinica: Optional[str] = None
    cama: Optional[str] = None
    sala: Optional[str] = None
    enabled: bool = True

