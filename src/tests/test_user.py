import json

import pytest
from fastapi import status

from ..app.db import users as user_repository
from starlette.testclient import TestClient
from ..app.utils import hashing
from ..app.api.schemas import User


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"email": "john", "password": "secret"}, status.HTTP_201_CREATED],
        [{"email": "john"}, status.HTTP_422_UNPROCESSABLE_ENTITY],
        [{"password": "secret"}, status.HTTP_422_UNPROCESSABLE_ENTITY],
        [{"password": "4let"}, status.HTTP_422_UNPROCESSABLE_ENTITY]
    ]
)
def test_create_user(test_app: TestClient, monkeypatch, payload, status_code):
    async def mock_create(user):
        return 1

    monkeypatch.setattr(user_repository, "create", mock_create)
    response = test_app.post("/users/", data=json.dumps(payload))
    assert response.status_code == status_code


def test_retrieve_user(test_app: TestClient, monkeypatch):
    test_user = {"id": 1, "email": "john"}

    async def mock_get_one(id):
        return test_user

    monkeypatch.setattr(user_repository, "get_one", mock_get_one)
    response = test_app.get("/users/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_user


def test_user_not_found(test_app: TestClient, monkeypatch):
    async def mock_get_one(id):
        return None

    monkeypatch.setattr(user_repository, "get_one", mock_get_one)
    response = test_app.get("/users/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "The user with id 1 was not found"


def test_user_hashing_password():
    password = "secret"
    hashed_password = hashing.bcrypt(password)
    assert hashing.verify(hashed_password, password)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"email": "some_existing_user", "password": "some_existing_password"}, status.HTTP_200_OK],
        [{"email": "john"}, status.HTTP_422_UNPROCESSABLE_ENTITY],
        [{"email": "some_existing_user", "password": "not_corresponding_password"}, status.HTTP_401_UNAUTHORIZED],
        [{"email": "not_existing_user", "password": "some_existing_password"}, status.HTTP_401_UNAUTHORIZED]
    ]
)
def test_user_credentials(test_app: TestClient, monkeypatch, payload, status_code):
    async def mock_check_credentials(credentials:User):
        if "email" in payload and "password" in payload:
            if payload["email"] == "some_existing_user" and payload["password"] == "some_existing_password":
                return True
        return False

    monkeypatch.setattr(user_repository, "check_credentials", mock_check_credentials)
    response = test_app.post("/users/credentials", data=json.dumps(payload))
    assert response.status_code == status_code


