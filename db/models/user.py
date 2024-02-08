from odmantic import Model

class User(Model):
    username: str
    enabled: bool = True
    password: str