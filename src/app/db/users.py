from fastapi.security import OAuth2PasswordRequestForm

from ..api.schemas import User
from .db_models import Users
from .db_engine import database
from ..utils import hashing


async def create(user: User):
    query = Users.insert().values(email=user.email, password=hashing.bcrypt(user.password))
    return await database.execute(query=query)


async def get_one(id: int):
    query = Users.select().where(id == Users.c.id)
    return await database.fetch_one(query=query)

async def get_one_by_name(email: str):
    query = Users.select().where(email == Users.c.email)
    return await database.fetch_one(query=query)

async def check_credentials(user: User):
    query = Users.select().where(Users.c.email == user.email)
    exists = await database.fetch_one(query=query)
    if not exists:
        return False
    password_ok = hashing.verify(exists.get("password"), user.password)
    print(password_ok)
    if not password_ok:
        return False
    return exists
