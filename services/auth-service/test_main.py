from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200


def test_login_with_wrong_credentials():
    response = client.post("/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_with_correct_credentials():
    response = client.post("/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user_id" in data


def test_refresh_with_invalid_token():
    response = client.post("/v1/auth/refresh", json={"refresh_token": "invalid-token"})
    assert response.status_code == 401