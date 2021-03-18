from pydantic import BaseModel, Field


class User(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

class PublicUser(BaseModel):
    id:int
    email:str