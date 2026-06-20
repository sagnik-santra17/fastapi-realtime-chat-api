from httpx import AsyncClient

#------------------Test helpers for user module-----------------#

#----helper function for user login-------#
async def get_token_from_logged_user(client: AsyncClient, username: str="test_user") -> dict:
    user_data = {
        "username": username,
        "email": f"{username}@email.com",
        "password": "test_password123",
        "confirm_password": "test_password123",
        "is_active": True
    }
    await client.post("/users/", json=user_data)

    login_credentials = {
        "username": username,
        "password": "test_password123"
    }
    login_response = await client.post("users/login", data=login_credentials)
    token_data = login_response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

#------------------ Test helpers for room id -----------------#
async def get_room_id(client: AsyncClient) -> int:
    room_data = {"room_name": "test_room"}
    response = await client.post(
        "/rooms/",
        json=room_data,
        headers=await get_token_from_logged_user(client)
    )
    data = response.json()
    room_id = data["room_id"]
    return room_id

#------------------ Test helpers for sender id -----------------#
async def get_sender_id(client: AsyncClient, username: str="test_user"):
    user_data = {
        "username": username,
        "email": f"{username}@email.com",
        "password": "test_password123",
        "confirm_password": "test_password123",
        "is_active": True
    }
    signup_response = await client.post("/users/", json=user_data)
    signup_data = signup_response.json()
    sender_id = signup_data["user_id"]

    login_credentials = {
        "username": username,
        "password": "test_password123"
    }
    login_response = await client.post("/users/login", data=login_credentials)
    token_data = login_response.json()
    access_token = token_data["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
        "sender_id": sender_id
    }


