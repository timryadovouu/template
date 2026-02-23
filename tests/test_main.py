from fastapi.testclient import TestClient  # type: ignore
from backend.main import app  # type: ignore


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_and_login():
    user_data = {"login": "user", "password": "user"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    login_data = {"username": "user", "password": "user"}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
