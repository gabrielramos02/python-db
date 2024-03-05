from odmantic import Model, Reference,Field, ObjectId
from typing import Optional

class Sala(Model):
    numero:str

class Cama(Model):
    numero:str
    ocupada: bool = False
    sala: Sala = Reference(key_name="id_sala")
    if ocupada:
        paciente: ObjectId
    
