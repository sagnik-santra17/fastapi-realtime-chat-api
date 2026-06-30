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
    login_response = await client.post("/users/login", data=login_credentials)
    token_data = login_response.json()

    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


#------------------ Test helpers for room id -----------------#

# No default parameter here—forces you to explicitly name the room in your tests
async def get_room_id(client: AsyncClient, headers: dict, room_name: str) -> int:
    room_data = {"room_name": room_name}
    response = await client.post(
        "/rooms/",
        json=room_data,
        headers=headers
    )
    
    data = response.json()
    return data["room_id"]


#------------------ Test helpers for sender id -----------------#

async def get_sender_id(client: AsyncClient, username: str="test_user") -> dict:
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
        "sender_id": sender_id,
        "user_id": sender_id  # Mapped so your test_caching.py file works perfectly
    }