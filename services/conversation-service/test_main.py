from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200


def test_create_conversation():
    response = client.post("/v1/conversations")
    assert response.status_code == 200
    assert "conversation_id" in response.json()


def test_get_nonexistent_conversation_history():
    response = client.get("/v1/conversations/00000000-0000-0000-0000-000000000000/history")
    assert response.status_code == 404


def test_get_nonexistent_task():
    response = client.get("/v1/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404