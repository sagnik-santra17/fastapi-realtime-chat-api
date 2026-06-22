# Global imports
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from starlette.websockets import WebSocketDisconnect

# Local imports
from app.main import app
from app.core.config import settings
from app.api.dependencies import get_message_dependency

client = TestClient(app)

# Creating a fake version of your database service
class MockMessageService:
    async def insert_message(self, message, sender_id, room_id):
        pass

# Creating a simple function to hand out the fake service
def get_mock_message_service():
    return MockMessageService()

# Swapping the real database dependency with the fake one
app.dependency_overrides[get_message_dependency] = get_mock_message_service

#--------------happy path tests----------------#

# ------------ Successful connection --------- #
def test_websocket_connection_success():
    token = {"sub": "1"}
    valid_token = jwt.encode(
        token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    with client.websocket_connect(f"/messages/ws/42?token={valid_token}") as websocket:
        assert websocket is not None

# ------------ Sending and receiving live messages --------- #
def test_websocket_send_and_receive():
    token = {"sub": "1"}
    valid_token = jwt.encode(
        token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    with client.websocket_connect(f"/messages/ws/42?token={valid_token}") as websocket:
        websocket.send_text(f"Hello, world!")
        message = websocket.receive_text()
        assert message == "User 1: Hello, world!"

# ------------ Keeping different chat rooms separated --------- #
def test_websocket_room_isolation():
    token_1 = {"sub": "1"}
    valid_token_1 = jwt.encode(
        token_1,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    token_2 = {"sub": "2"}
    valid_token_2 = jwt.encode(
        token_2,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    with client.websocket_connect(f"/messages/ws/42?token={valid_token_1}") as ws_1:
        with client.websocket_connect(f"/messages/ws/99?token={valid_token_2}") as ws_2:
            ws_1.send_text(f"Message to room 42")
            ws_2.send_text(f"Message to room 99")

            message = ws_2.receive_text()
            assert message == "User 2: Message to room 99"


# -------------- sad path tests ----------------#

# ------------ Blocking invalid tokens --------- #
def test_websocket_connect_bad_token():
    token = "invalid_token"

    with pytest.raises(WebSocketDisconnect) as exception_info:
        with client.websocket_connect(f"/messages/ws/42?token={token}"):
            pass
    assert exception_info.value.code == 1008

# ------------ Blocking requests missing a token --------- #
def test_websocket_connect_missing_token():
    with pytest.raises(WebSocketDisconnect) as exception_info:
        with client.websocket_connect(f"/messages/ws/42"):
            pass
    assert exception_info.value.code == 1008

# ------------ Blocking invalid room ID formats --------- #
def test_websocket_connect_invalid_room_id_type():
    token = {"sub": "1"}
    valid_token = jwt.encode(
        token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    invalid_room_id = "invalid_room_id"

    with (pytest.raises(WebSocketDisconnect) as exception_info):
        with client.websocket_connect(f"/messages/ws/{invalid_room_id}?token={valid_token}"):
            pass
    assert exception_info.value.code == 1008