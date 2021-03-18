from pydantic import BaseModel, Field


class User(BaseModel):
    email: str = Field(...)
    password: str = Field(..., min_length=5)

class PublicUser(BaseModel):
    id:int
    email:str