from odmantic import Model
from typing import Optional

class User(Model):
    username: str
    enabled: bool = True
    password: str
    role: Optional[str] = None