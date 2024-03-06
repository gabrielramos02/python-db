from db.client import db_client
from db.models.imports import Cama,Sala

async def obtener_cama(cama: str,sala:str):
    sala_db = await db_client.find_one(Sala,Sala.numero == sala)
    cama_db = await db_client.find_one(Cama, (Cama.numero == cama)&(Cama.sala == sala_db.id))
    return cama_db