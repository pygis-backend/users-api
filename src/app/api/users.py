from typing import List

from ..db import users as user_repository
from .schemas import User, PublicUser
from fastapi import APIRouter, HTTPException, Path, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

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
async def get_user(id: int):
    user = await user_repository.get_one(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user with id {id} was not found")
    return user


@router.post("/credentials", status_code=status.HTTP_200_OK)
async def check_user_credentials(request: User):
    valid_credentials = await user_repository.check_credentials(request)
    if not valid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

