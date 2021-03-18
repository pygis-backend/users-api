from typing import List

from ..db import users as user_repository
from .schemas import User, PublicUser
from fastapi import APIRouter, HTTPException, Path, status

router = APIRouter()


@router.post("/", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def create_user(payload: User):
    user_id = await user_repository.create(payload)
    user = await user_repository.get_one(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occured during user creation")
    return user

@router.get("/{id}", response_model=PublicUser, status_code=status.HTTP_200_OK)
async def get_user(id:int):
    user = await user_repository.get_one(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user with id {id} was not found")
    return user