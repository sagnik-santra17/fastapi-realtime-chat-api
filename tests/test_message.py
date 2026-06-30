import pytest
from fastapi import status
from app.api.dependencies import RateLimiter
from tests.test_helper import get_room_id, get_sender_id


# Automatically disables all Redis rate limit tracking
@pytest.fixture(autouse=True)
def disable_rate_limits(monkeypatch):
    async def mock_check(*args, **kwargs):
        return None
    monkeypatch.setattr(RateLimiter, "check_rate_limit", mock_check)


#--------------happy path tests----------------#

#--------Create message test success---------#
@pytest.mark.asyncio
async def test_create_message_success(client):
    sender_data = await get_sender_id(client, username="msg_create")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_create") 

    new_message = {"content": "new test message"}
    response = await client.post(
        f"/messages/?room_id={room_id}",
        json=new_message,
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "new test message"
    assert "message_id" in data
    assert "room_id" in data
    assert "sender_id" in data
    assert "sent_at" is not None

#--------Get message history test success---------#
@pytest.mark.asyncio
async def test_get_messages_success(client):
    sender_data = await get_sender_id(client, username="msg_hist")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_hist")

    for i in range(5):
        new_message = {"content": f"new test message {i}"}
        await client.post(
            f"/messages/?room_id={room_id}",
            json=new_message,
            headers=headers
        )
    response = await client.get(
        f"/messages/?room_id={room_id}&limit=50",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for message in data:
        assert "message_id" in message

#--------Get message history with limit test success---------#
@pytest.mark.asyncio
async def test_get_messages_with_limit_success(client):
    sender_data = await get_sender_id(client, username="msg_limit")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_limit")

    for i in range(5):
        new_message = {"content": f"new test message {i}"}
        await client.post(
            f"/messages/?room_id={room_id}",
            json=new_message,
            headers=headers
        )
    response = await client.get(
        f"/messages/?room_id={room_id}&limit=2",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for message in data:
        assert "message_id" in message

# -------- Get message history for empty room test success --------- #
@pytest.mark.asyncio
async def test_get_messages_empty_room_success(client):
    sender_data = await get_sender_id(client, username="msg_empty")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_empty")

    response = await client.get(
        f"/messages/?room_id={room_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


# -------------- sad path tests ----------------#

# -------- Create message with missing room test failure --------- #
@pytest.mark.asyncio
async def test_create_message_room_not_found_failure(client):
    sender_data = await get_sender_id(client, username="msg_noroom")
    room_id = 9999999999
    headers = {"Authorization": sender_data["Authorization"]}

    new_message = {"content": "new test message"}

    response = await client.post(
        f"/messages/?room_id={room_id}",
        headers=headers,
        json=new_message
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to find room"}

# --------Create message with empty content test failure---------#
@pytest.mark.asyncio
async def test_create_message_empty_content_failure(client):
    sender_data = await get_sender_id(client, username="msg_nocontent")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_nocontent")

    new_message = {"content": ""}
    response = await client.post(
        f"/messages/?room_id={room_id}",
        json=new_message,
        headers=headers
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

# -------- Create message with content too long test failure --------- #
@pytest.mark.asyncio
async def test_create_message_content_too_long_failure(client):
    sender_data = await get_sender_id(client, username="msg_toolong")
    headers = {"Authorization": sender_data["Authorization"]}

    # Pass a unique room_name to the helper
    room_id = await get_room_id(client, headers=headers, room_name="rm_toolong")

    msg = "x" * 2001
    new_message = {"content": msg}
    response = await client.post(
        f"/messages/?room_id={room_id}",
        json=new_message,
        headers=headers
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

# -------- Get message history with invalid room ID type test failure --------- #
@pytest.mark.asyncio
async def test_get_messages_room_not_found_failure(client):
    room_id = 9999999999999999
    # Shortened username to pass validation
    sender_data = await get_sender_id(client, username="msg_hist_fail")
    headers = {"Authorization": sender_data["Authorization"]}

    response = await client.get(
        f"/messages/?room_id={room_id}&limit=50",
        headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to find room"}