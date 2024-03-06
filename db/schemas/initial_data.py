from db.client import db_client
from db.models.imports import Cama,Sala


async def valores_iniciales():
    salas_existe = await db_client.find(Sala)
    if salas_existe.__len__() != 0 :
        return
    salas = []
    camas = []
    for numero_sala in range (1,21):
        sala = Sala(numero=str(numero_sala))
        salas.append(sala)
        camas = []
        for cama_actual in range(1,11):
            cama = Cama(numero=str(cama_actual),paciente=None,sala=sala)
            camas.append(cama)
            await db_client.save_all(camas)
    await db_client.save_all(salas)
    
    return




