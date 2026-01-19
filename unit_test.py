from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# tests if server is running or not
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "System Order is Running"}
