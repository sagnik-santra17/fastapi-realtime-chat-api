# Global imports
import pytest
# Local imports
from tests.test_helper import get_token_from_logged_user


@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Chat-room API"}

# ---------- Happy tests -----------#

# --------user sign up test--------#
@pytest.mark.asyncio
async def test_register_user_success(client):
    user_data = {
        "username": "test_user",
        "email": "test_user@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "is_active": True,
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "test_user"
    assert data["email"] == "test_user@email.com"
    assert data["is_active"] is True
    assert "user_id" in data
    assert "password" not in data

# --------user log in test--------#
@pytest.mark.asyncio
async def test_user_login_success(client):
    user_data = {
        "username": "test_user",
        "email": "test_user@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "is_active": True,
    }
    await client.post("/users/", json=user_data)

    login_credentials = {"username": "test_user", "password": "test_password"}
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data

# --------user delete test--------#
@pytest.mark.asyncio
async def test_user_delete_user_success(client):
    headers = await get_token_from_logged_user(client)
    delete_data = {"password": "test_password123"}

    response = await client.request(
        "DELETE", "/users/me", headers=headers, json=delete_data
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "User account deleted successfully"}

# --------user update test--------#
@pytest.mark.asyncio
async def test_user_update_user_success(client):
    headers = await get_token_from_logged_user(client)
    update_data = {
        "username": "test_user1",
        "email": "test_user1@email.com",
        "password": "new_test_password123",
        "confirm_password": "new_test_password123",
        "current_password": "test_password123",
    }
    response = await client.patch("/users/me", headers=headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user1"
    assert data["email"] == "test_user1@email.com"
    assert "password" not in data

# --------user view profile test--------#
@pytest.mark.asyncio
async def test_view_user_profile_success(client):
    headers = await get_token_from_logged_user(client)
    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["username"] == "test_user"
    assert data["email"] == "test_user@email.com"

# ---------- Sad tests -----------#

# --------username already exists fail--------#
@pytest.mark.asyncio
async def test_username_exists_fail(client):
    await get_token_from_logged_user(client)

    user_data = {
        "username": "test_user",
        "email": "new_test_user@email.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True,
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 409
    error_message = response.json()["detail"]
    assert "User with username test_user already exists" in error_message

# --------Email already exists fail--------#
@pytest.mark.asyncio
async def test_email_exists_fail(client):
    await get_token_from_logged_user(client)

    user_data = {
        "username": "new_test_user",
        "email": "test_user@email.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True,
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 409
    error_message = response.json()["detail"]
    assert "User with email test_user@email.com already exists" in error_message

# --------Invalid email format signup fail--------#
@pytest.mark.asyncio
async def test_register_invalid_email_fail(client):
    user_data = {
        "username": "bad_email_user",
        "email": "not-a-real-email",
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True,
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 422

# --------Passwords didn't match during sign up--------#
@pytest.mark.asyncio
async def test_passwords_mismatch_signup_fail(client):
    user_data = {
        "username": "new_test_user",
        "email": "new_test_user@email.com",
        "password": "password123",
        "confirm_password": "not_password123",
        "is_active": True,
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 422
    error_message = response.json()["detail"][0]["msg"]
    assert "Passwords don't match" in error_message

# --------Wrong username during log in--------#
@pytest.mark.asyncio
async def test_wrong_username_login_fail(client):
    login_credentials = {
        "username": "wrong_test_user",
        "password": "test_password123",
    }
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# --------Wrong password during log in--------#
@pytest.mark.asyncio
async def test_wrong_password_login_fail(client):
    login_credentials = {"username": "test_user", "password": "wrong_password123"}
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# --------Update profile unauthorized fail--------#
@pytest.mark.asyncio
async def test_update_user_unauthorized_fail(client):
    update_data = {"username": "hacker_username", "email": "hacker@email.com"}
    response = await client.patch("/users/me", json=update_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# --------Delete account unauthorized fail--------#
@pytest.mark.asyncio
async def test_delete_user_unauthorized_fail(client):
    delete_data = {"password": "hacker_password"}
    response = await client.request("DELETE", "/users/me", json=delete_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# --------view account unauthorized fail--------#
@pytest.mark.asyncio
async def test_view_profile_unauthorized_fail(client):
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# --------Wrong password error for updating user--------#
@pytest.mark.asyncio
async def test_update_user_wrong_current_password_unauthorized(client):
    headers = await get_token_from_logged_user(client)
    update_data = {"username": "new_name", "current_password": "wrong_password"}
    response = await client.patch("/users/me", headers=headers, json=update_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect current password."

# --------Wrong password error for deleting user--------#
@pytest.mark.asyncio
async def test_delete_user_wrong_password_unauthorized(client):
    headers = await get_token_from_logged_user(client)
    delete_data = {"password": "wrong_password"}
    response = await client.request(
        "DELETE", "/users/me", headers=headers, json=delete_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password. Account deletion aborted."

# --------Update username already exists conflict--------#
@pytest.mark.asyncio
async def test_update_username_already_exists_conflict(client):
    await get_token_from_logged_user(client, username="user_b")
    headers_a = await get_token_from_logged_user(client, username="user_a")
    update_data = {"username": "user_b", "current_password": "test_password123"}
    response = await client.patch("/users/me", headers=headers_a, json=update_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

# --------Update email already exists conflict--------#
@pytest.mark.asyncio
async def test_update_email_already_exists_conflict(client):
    await get_token_from_logged_user(client, username="user_b")

    headers_a = await get_token_from_logged_user(client, username="user_a")
    update_data = {"email": "user_b@email.com", "current_password": "test_password123"}
    response = await client.patch("/users/me", headers=headers_a, json=update_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

# --------Passwords didn't match during profile update--------#
@pytest.mark.asyncio
async def test_passwords_mismatch_update_fail(client):
    headers = await get_token_from_logged_user(client)
    update_data = {
        "password": "new_password",
        "confirm_password": "mismatched_password",
        "current_password": "test_password123",
    }
    response = await client.patch("/users/me", headers=headers, json=update_data)
    assert response.status_code == 422
    assert "Passwords don't match" in response.json()["detail"][0]["msg"]