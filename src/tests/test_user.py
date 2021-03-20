import json
import os

import pytest
from fastapi import status

from ..app.db import users as user_repository
from starlette.testclient import TestClient
from ..app.utils import hashing
from ..app.api.schemas import User


@pytest.mark.parametrize(
    "payload, status_code, api_key",
    [
        [{"email": "john", "password": "secret"}, status.HTTP_201_CREATED, os.getenv("API_KEY")],
        [{"email": "john", "password": "secret"}, status.HTTP_401_UNAUTHORIZED, None],
        [{"email": "john"}, status.HTTP_422_UNPROCESSABLE_ENTITY, os.getenv("API_KEY")],
        [{"password": "secret"}, status.HTTP_422_UNPROCESSABLE_ENTITY, os.getenv("API_KEY")],
        [{"password": "4let"}, status.HTTP_422_UNPROCESSABLE_ENTITY, os.getenv("API_KEY")]
    ]
)
def test_create_user(test_app: TestClient, monkeypatch, payload, status_code, api_key):
    async def mock_create(user):
        return 1

    async def mock_get_one(id):
        return {"id": 1, "email": "john", "password": "secret"}

    test_app.headers[os.getenv("API_KEY_NAME")] = api_key
    monkeypatch.setattr(user_repository, "create", mock_create)
    monkeypatch.setattr(user_repository, "get_one", mock_get_one)
    response = test_app.post("/users/", data=json.dumps(payload))
    assert response.status_code == status_code


def test_retrieve_user(test_app: TestClient, monkeypatch):
    test_user = {"id": 1, "email": "john"}

    async def mock_get_one(id):
        return test_user

    test_app.headers[os.getenv("API_KEY_NAME")] = os.getenv("API_KEY")
    monkeypatch.setattr(user_repository, "get_one", mock_get_one)
    response = test_app.get("/users/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_user


def test_user_not_found(test_app: TestClient, monkeypatch):
    async def mock_get_one(id):
        return None

    test_app.headers[os.getenv("API_KEY_NAME")] = os.getenv("API_KEY")
    monkeypatch.setattr(user_repository, "get_one", mock_get_one)
    response = test_app.get("/users/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "The user with id 1 was not found"


def test_user_hashing_password():
    password = "secret"
    hashed_password = hashing.bcrypt(password)
    assert hashing.verify(hashed_password, password)


@pytest.mark.parametrize(
    "payload, status_code, api_key",
    [
        [{"email": "some_existing_user", "password": "some_existing_password"}, status.HTTP_401_UNAUTHORIZED,
         os.getenv("API_KEY")],
        [{"email": "john"}, status.HTTP_422_UNPROCESSABLE_ENTITY, os.getenv("API_KEY")],
        [{"email": "some_existing_user", "password": "not_corresponding_password"}, status.HTTP_401_UNAUTHORIZED,
         os.getenv("API_KEY")],
        [{"email": "not_existing_user", "password": "some_existing_password"}, status.HTTP_401_UNAUTHORIZED,
         os.getenv("API_KEY")],
        [{"email": "not_existing_user", "password": "some_existing_password"}, status.HTTP_401_UNAUTHORIZED, None]
    ]
)
def test_user_credentials(test_app: TestClient, monkeypatch, payload, status_code, api_key):
    async def mock_check_credentials(credentials: User):
        if "email" in payload and "password" in payload:
            if payload["email"] == "some_existing_user" and payload["password"] == "some_existing_password":
                return True
        return False

    monkeypatch.setattr(user_repository, "check_credentials", mock_check_credentials)
    test_app.headers[os.getenv("API_KEY_NAME")] = api_key
    response = test_app.post("/users/credentials", data=json.dumps(payload))
    assert response.status_code == status_code
