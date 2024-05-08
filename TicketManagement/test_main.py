from fastapi.testclient import TestClient
from TicketManagement.main import app
def test_read_main():

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
@pytest.mark.parametrize("token, expected", [
    (jwt.encode({"ticket_id": "123"}, SECRET_KEY), {"ticket_id": "123", "message": "Ticket verified successfully"}),
    (jwt.encode({"ticket_id": "456", "valid_date": datetime.today()}, SECRET_KEY), {"ticket_id": "456", "message": "Ticket verified successfully"}),
    (jwt.encode({"ticket_id": "789", "valid_date": datetime.today() - timedelta(days=1)}, SECRET_KEY), HTTPException),
    ("invalid", HTTPException),
])
def test_verify_ticket(token, expected):
    if isinstance(expected, dict):
        assert verify_ticket(token) == expected
    else:
        with pytest.raises(expected):
            verify_ticket(token)

def test_verify_ticket_no_ticket_id():
    token = jwt.encode({"user_id": "123"}, SECRET_KEY)
    with pytest.raises(HTTPException):
        verify_ticket(token)

def test_verify_ticket_extra_claims():
    token = jwt.encode({"ticket_id": "123", "user_id": "456"}, SECRET_KEY)
    assert verify_ticket(token) == {"ticket_id": "123", "message": "Ticket verified successfully"}
def test_verify_ticket_valid_token():
    token = jwt.encode({"ticket_id": "123", "valid_date": datetime.today()}, SECRET_KEY)
    assert verify_ticket(token) == {"ticket_id": "123", "message": "Ticket verified successfully"}

def test_verify_ticket_expired_token():
    token = jwt.encode({"ticket_id": "123", "valid_date": datetime.today() - timedelta(days=1)}, SECRET_KEY)
    with pytest.raises(HTTPException) as exc_info:
        verify_ticket(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Ticket expired"

def test_verify_ticket_missing_ticket_id():
    token = jwt.encode({"user_id": "123"}, SECRET_KEY)
    with pytest.raises(HTTPException) as exc_info:
        verify_ticket(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"

def test_verify_ticket_invalid_token():
    token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        verify_ticket(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
