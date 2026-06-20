import pytest

from tests.test_helper import get_room_id, get_sender_id


#--------------happy path tests----------------#

#--------Create message test success---------#
@pytest.mark.asyncio
async def test_create_message_success(client):
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    new_message = {"content": "new test message"}
    response = await client.post(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
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
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    for i in range(10):
        new_message = {"content": f"new test message {i}"}
        await client.post(
            f"/messages/?room_id={room_id}&sender_id={sender_id}",
            json=new_message,
            headers=headers
        )
    response = await client.get(
        f"/messages/?room_id={room_id}&sender_id={sender_id}&limit=50",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    for message in data:
        assert "message_id" in message

#--------Get message history with limit test success---------#
@pytest.mark.asyncio
async def test_get_messages_with_limit_success(client):
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    for i in range(100):
        new_message = {"content": f"new test message {i}"}
        await client.post(
            f"/messages/?room_id={room_id}&sender_id={sender_id}",
            json=new_message,
            headers=headers
        )
    response = await client.get(
        f"/messages/?room_id={room_id}&sender_id={sender_id}&limit=50",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 50
    for message in data:
        assert "message_id" in message

# -------- Get message history for empty room test success --------- #
@pytest.mark.asyncio
async def test_get_messages_empty_room_success(client):
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    response = await client.get(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


# -------------- sad path tests ----------------#

# -------- Create message with missing room test failure --------- #
@pytest.mark.asyncio
async def test_create_message_room_not_found_failure(client):
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    room_id = 9999999999
    headers = {"Authorization": sender_data["Authorization"]}
    new_message = {"content": "new test message"}

    response = await client.post(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
        headers=headers,
        json=new_message
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to find room"}


# -------- Create message with missing sender test failure --------- #
@pytest.mark.asyncio
async def test_create_message_sender_not_found_failure(client):
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = 999999999999
    room_id = await get_room_id(client)
    headers = {"Authorization": sender_data["Authorization"]}

    new_message = {"content": "new test message"}
    response = await client.post(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
        headers=headers,
        json=new_message
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to find user"}


# --------Create message with empty content test failure---------#
@pytest.mark.asyncio
async def test_create_message_empty_content_failure(client):
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    new_message = {"content": ""}
    response = await client.post(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
        json=new_message,
        headers=headers
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

# -------- Create message with content too long test failure --------- #
@pytest.mark.asyncio
async def test_create_message_content_too_long_failure(client):
    room_id = await get_room_id(client)
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    msg = "x" * 2001
    new_message = {"content": msg}
    response = await client.post(
        f"/messages/?room_id={room_id}&sender_id={sender_id}",
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
    sender_data = await get_sender_id(client, username="new_sender")
    sender_id = sender_data["sender_id"]
    headers = {"Authorization": sender_data["Authorization"]}

    response = await client.get(
        f"/messages/?room_id={room_id}&sender_id={sender_id}&limit=50",
        headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to find room"}
