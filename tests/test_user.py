#Global imports
import pytest
#Local imports
from tests.test_helper import get_token_from_logged_user


@pytest.mark.asyncio
async def test_read_root(client): #test 1
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Chat-room API"}

#--------------happy path tests----------------#

#--------user sign up test--------#
@pytest.mark.asyncio
async def test_register_user_success(client): #test 2
    user_data = {
        "username": "test_user",
        "email": "test_user@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "is_active": True
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "test_user"
    assert data["email"] == "test_user@email.com"
    assert data["is_active"] is True
    assert "user_id" in data
    assert "password" not in data

#----------user log in test--------#
@pytest.mark.asyncio
async def test_user_login_success(client): #test 3
    user_data = {
        "username": "test_user",
        "email": "test_user@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "is_active": True
    }
    await client.post("/users/", json=user_data)

    login_credentials = {
        "username": "test_user",
        "password": "test_password"
    }
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data

#----------user delete test--------#
@pytest.mark.asyncio
async def test_user_delete_user_success(client): #test 4
    headers = await get_token_from_logged_user(client)
    delete_data = {"password": "test_password123"}

    response = await client.request("DELETE", "/users/me", headers=headers, json=delete_data)
    assert response.status_code == 200
    assert response.json() == {"detail": "User account deleted successfully"}

#----------user update test----------#
@pytest.mark.asyncio
async def test_user_update_user_success(client): #test 5
    headers = await get_token_from_logged_user(client)
    update_data = {
        "username": "test_user1",
        "email": "test_user1@email.com",
        "password": "new_test_password123",
        "confirm_password": "new_test_password123",
        "current_password": "test_password123",
    }
    response = await client.patch("/users/me", headers=headers,  json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user1"
    assert data["email"] == "test_user1@email.com"
    assert "password" not in data

#-----------user view profile test------------#
@pytest.mark.asyncio
async def test_view_user_profile_success(client): #test 6
    headers = await get_token_from_logged_user(client)
    await client.get("/users/me", headers=headers)

    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["username"] == "test_user"
    assert data["email"] == "test_user@email.com"


#-----------------Unhappy tests---------------------#

#-------username already exists fail-------#
@pytest.mark.asyncio
async def test_username_exists_fail(client): #test 7
    await get_token_from_logged_user(client)

    user_data = {
        "username": "test_user",
        "email": "new_test_user@email.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 409
    error_message = response.json()["detail"]
    assert "User with username test_user already exists" in error_message

#-------Email already exists fail-------#
@pytest.mark.asyncio
async def test_email_exists_fail(client): #test 8
    await get_token_from_logged_user(client)

    user_data = {
        "username": "new_test_user",
        "email": "test_user@email.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 409
    error_message = response.json()["detail"]
    assert "User with email test_user@email.com already exists" in error_message

# -------Invalid email format signup fail-------#
@pytest.mark.asyncio
async def test_register_invalid_email_fail(client): #test 9
    user_data = {
        "username": "bad_email_user",
        "email": "not-a-real-email",  # <--- broken email format
        "password": "password123",
        "confirm_password": "password123",
        "is_active": True
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 422

#-------Passwords didn't match during sign up--------#
@pytest.mark.asyncio
async def test_passwords_mismatch_signup_fail(client): #test 10
    user_data = {
        "username": "new_test_user",
        "email": "new_test_user@email.com",
        "password": "password123",
        "confirm_password": "not_password123",
        "is_active": True
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 422
    error_message = response.json()["detail"][0]["msg"]
    assert "Passwords don't match" in error_message

#-------Wrong username during log in--------#
@pytest.mark.asyncio
async def test_wrong_username_login_fail(client): #test 11
    login_credentials = {
        "username": "wrong_test_user",
        "password": "test_password123"
    }
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

#-------Wrong password during log in--------#
@pytest.mark.asyncio
async def test_wrong_password_login_fail(client): #test 12
    login_credentials = {
        "username": "test_user",
        "password": "wrong_password123"
    }
    response = await client.post("/users/login", data=login_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# -------Update profile unauthorized fail-------#
@pytest.mark.asyncio
async def test_update_user_unauthorized_fail(client): #test 13
    update_data = {
        "username": "hacker_username",
        "email": "hacker@email.com"
    }
    response = await client.patch("/users/me", json=update_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# -------Delete account unauthorized fail-------#
@pytest.mark.asyncio
async def test_delete_user_unauthorized_fail(client): #test 14
    delete_data = {"password": "hacker_password"}
    response = await client.request("DELETE", "/users/me", json=delete_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# -------view account unauthorized fail-------#
@pytest.mark.asyncio
async def test_view_profile_unauthorized_fail(client): #test 15
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
