from ..api.schemas import User
from .db_models import Users
from .db_engine import database
from ..utils import hashing
from ..utils.logs import log_sql_query


async def create(user: User):
    query = Users.insert().values(username=user.username, password=hashing.bcrypt(user.password))
    log_sql_query(query)
    return await database.execute(query=query)


async def get_one(user_id: int):
    query = Users.select().where(user_id == Users.c.id)
    user_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(user_found))
    return user_found[0] if len(user_found) > 0 else None


async def get_one_by_name(username: str):
    query = Users.select().where(username == Users.c.username)
    user_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(user_found))
    return user_found[0] if len(user_found) > 0 else None


async def check_credentials(user: User):
    query = Users.select().where(Users.c.username == user.username)
    user_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(user_found))
    if not len(user_found) == 0:
        return False
    password_ok = hashing.verify(user_found[0].get("password"), user.password)
    if not password_ok:
        return False
    return user_found
