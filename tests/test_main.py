from fastapi.testclient import TestClient  # type: ignore
from backend.main import app  # type: ignore
import pytest  # type: ignore

client = TestClient(app)


# def test_health_check():
#     response = client.get("/health")
#     assert response.status_code == 200
#     assert response.json() == {"status": "ok"}


# def test_register_and_login():
#     user_data = {"login": "user", "password": "user"}
#     response = client.post("/register", json=user_data)
#     assert response.status_code == 200
#     assert "access_token" in response.json()

#     login_data = {"username": "user", "password": "user"}
#     response = client.post("/login", data=login_data)
#     assert response.status_code == 200
#     assert "access_token" in response.json()

@pytest.fixture
def test_user():
    user_data = {
        "login": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "role": "user"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"token": token, "login": "testuser"}

@pytest.fixture
def second_user():
    user_data = {
        "login": "anotheruser",
        "email": "another@example.com",
        "password": "testpassword123",
        "first_name": "Another",
        "last_name": "User",
        "phone": "0987654321",
        "role": "user"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"token": token, "login": "anotheruser"}

@pytest.fixture
def auth_headers(test_user):
    return {"Authorization": f"Bearer {test_user['token']}"}

@pytest.fixture
def another_auth_headers(second_user):
    return {"Authorization": f"Bearer {second_user['token']}"}

@pytest.fixture
def sample_post(auth_headers):
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content"
    }
    response = client.post("/api/posts", json=post_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()