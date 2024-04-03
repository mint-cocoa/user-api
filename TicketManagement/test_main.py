from fastapi.testclient import TestClient
from TicketManagement.main import app
def test_read_main():

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}