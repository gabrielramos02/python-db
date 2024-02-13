# Funciones para eliminar la contrase;a al devolver usuario
from db.models.user import User

def password_free(user: User) -> User:
    del user.password
    return user


def password_free_all(users: list[User]):
    for user in users:
        del user.password
    return users

