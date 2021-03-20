from fastapi import FastAPI

from .api import monitor, users
from .db.db_engine import engine, database
from .db.db_models import metadata

metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(monitor.router, prefix="/monitor", tags=["monitoring"])
app.include_router(users.router, prefix="/users", tags=["notes"])
