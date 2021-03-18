from starlette.testclient import TestClient
from fastapi import status
def test_ping(test_app:TestClient):
    response = test_app.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping":"pong"}