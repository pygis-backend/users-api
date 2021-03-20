import os
from typing import List

from ..db import users as user_repository
from .schemas import User, PublicUser
from fastapi import APIRouter, HTTPException, status, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey


API_KEY = os.getenv("API_KEY")
API_KEY_NAME = os.getenv("API_KEY_NAME")

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):

    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )
router = APIRouter()


@router.post("/", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def create_user(payload: User, api_key: APIKey = Depends(get_api_key)):
    user_id = await user_repository.create(payload)
    user = await user_repository.get_one(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occured during user creation")
    return user


@router.get("/{id}", response_model=PublicUser, status_code=status.HTTP_200_OK)
async def get_user(id: int, api_key: APIKey = Depends(get_api_key)):
    user = await user_repository.get_one(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user with id {id} was not found")
    return user


@router.post("/credentials", status_code=status.HTTP_200_OK)
async def check_user_credentials(request: User, api_key: APIKey = Depends(get_api_key)):
    valid_credentials = await user_repository.check_credentials(request)
    if not valid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

