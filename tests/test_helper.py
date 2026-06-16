from httpx import AsyncClient

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


