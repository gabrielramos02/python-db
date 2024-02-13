from odmantic import Model
from datetime import date


class Paciente(Model):
    name: str
    surname: str
    fecha_ingreso: str = str(date.today())
    historia_clinica: str
    cama: str
    sala: str
    enabled: bool = True
