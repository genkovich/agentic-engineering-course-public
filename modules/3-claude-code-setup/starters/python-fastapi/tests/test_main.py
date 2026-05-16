"""Базовий тест для FastAPI Hello World."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_returns_hello() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "agentic-engineering-course" in body["message"]


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["uptime"], int | float)
