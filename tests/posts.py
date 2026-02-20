import pytest  # type: ignore
from fastapi.testclient import TestClient  # type: ignore
from backemd.main import app  # type: ignore

client = TestClient(app)

def test_like_post_not_found():
    response = client.post("/api/posts/999/like")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"