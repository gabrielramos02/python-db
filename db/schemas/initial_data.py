from db.client import db_client
from db.models.imports import Cama, Sala, User
from passlib.context import CryptContext

crypth = CryptContext(schemes=["bcrypt"])


async def valores_iniciales():
    salas_existe = await db_client.find(Sala)
    director_existe = await db_client.find(User)
    if director_existe.__len__() == 0:
        director = User(
            username="director", password=crypth.encrypt("director"), role="director"
        )
        await db_client.save(director)
    if salas_existe.__len__() != 0:
        return
    salas = []
    camas = []
    for numero_sala in range(1, 21):
        sala = Sala(numero=str(numero_sala))
        salas.append(sala)
        camas = []
        for cama_actual in range(1, 11):
            cama = Cama(numero=str(cama_actual), paciente=None, sala=sala)
            camas.append(cama)
            await db_client.save_all(camas)
    sala_vacia = Sala(numero="vacia")

    cama_vacia = Cama(numero="vacia", paciente=None, sala=sala_vacia, ocupada=True)
    await db_client.save(cama_vacia)
    salas.append(sala_vacia)
    await db_client.save_all(salas)

    return
