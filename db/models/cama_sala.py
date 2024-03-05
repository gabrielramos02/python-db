from odmantic import Model, Reference,Field
from db.models.paciente import Paciente
from typing import Optional


class Sala(Model):
    numero:str

class Cama(Model):
    numero:str
    ocupada: bool = False
    paciente: Paciente = Reference(key_name="id_paciente")
    sala: Sala = Reference(key_name="id_sala")
    
