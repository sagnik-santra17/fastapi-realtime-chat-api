#global imports
import pytest
#local imports
from tests.test_helper import get_token_from_logged_user, get_room_id

#--------------happy path tests----------------#

#--------Create room test success---------#
@pytest.mark.asyncio
async def test_create_room_success(client):
    headers = await get_token_from_logged_user(client)

    room_data = {"room_name": "test_room"}
    response = await client.post("/rooms/", headers=headers, json=room_data)
    assert response.status_code == 201

    data = response.json()
    assert data["room_name"] == "test_room"
    assert data["created_at"] is not None
    assert "room_id" in data

#--------Delete room test success---------#
@pytest.mark.asyncio
async def test_delete_room_success(client):
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)
    delete_data = {"current_password": "test_password123"}

    response = await client.request("DELETE", f"/rooms/{room_id}", json=delete_data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"Room has been deleted successfully!"}

#--------Update room test success---------#
@pytest.mark.asyncio
async def test_update_room_success(client):
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)
    update_data = {
        "room_name": "updated_test_room",
        "current_password": "test_password123"
    }
    response = await client.patch(f"/rooms/{room_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["room_name"] == "updated_test_room"
    assert data["created_at"] is not None
    assert "room_id" in data

#---------Get details of one room------#
@pytest.mark.asyncio
async def test_get_one_room_details_success(client):
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)
    response = await client.get(f"/rooms/{room_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["room_name"] == "test_room"
    assert data["created_at"] is not None
    assert "room_id" in data

#------Get details of all rooms-------#
@pytest.mark.asyncio
async def test_get_all_room_details_success(client):
    headers = await get_token_from_logged_user(client)

    for i in range(25):
        room_data = {
            "room_name": f"test_room_{i}",
        }
        await client.post("/rooms/", headers=headers, json=room_data)

    response = await client.get("/rooms/?skip=0&limit=20", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 20
    for i in range(20):
        assert data[i]["room_name"] == f"test_room_{i}"
        assert data[i]["created_at"] is not None
        assert "room_id" in data[i]

#------Get details of all rooms (page 2)-------#
@pytest.mark.asyncio
async def test_get_room_details_next_page_success(client):
    headers = await get_token_from_logged_user(client)

    for i in range(25):
        room_data = {
            "room_name": f"test_room_{i}",
        }
        await client.post("/rooms/", headers=headers, json=room_data)

    # Skip the first 20 rooms, look at the rest
    response = await client.get("/rooms/?skip=20&limit=20", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # There are exactly 5 rooms left over (25 - 20 = 5)
    assert len(data) == 5
    for i in range(5):
        #The remaining rooms are named 20, 21, 22, 23, and 24
        actual_index = 20 + i
        assert data[i]["room_name"] == f"test_room_{actual_index}"
        assert data[i]["created_at"] is not None
        assert "room_id" in data[i]

#-------------------- Unhappy tests ---------------------#

#-------- user tries access rooms without logging in --------#
@pytest.mark.parametrize("method, path", [
    ("POST", "/rooms/"),
    ("GET", "/rooms/"),
    ("GET", "/rooms/1"),
    ("PATCH", "/rooms/1"),
    ("DELETE", "/rooms/1")
])
@pytest.mark.asyncio
async def test_room_endpoints_unauthorized_401(client, method, path):
    response = await client.request(method, path)
    assert response.status_code == 401

#-------- Bad input test ------#
@pytest.mark.parametrize("bad_data", [
    # Case 1: Too short room name
    {"room_name": "xx"},
    # Case 2: Missing room name
    {"room_name": ""}
])
@pytest.mark.asyncio
async def test_room_endpoints_bad_input_data(client, bad_data):
    headers = await get_token_from_logged_user(client)
    response = await client.post("/rooms/", json=bad_data, headers=headers)
    assert response.status_code == 422

#--------- Duplicate room name test ---------#
@pytest.mark.asyncio
async def test_create_room_duplicate_name_conflict(client):
    headers = await get_token_from_logged_user(client)
    room_data = {"room_name": "test_room"}

    # Creating the first room
    first_response = await client.post("/rooms/", headers=headers, json=room_data)
    assert first_response.status_code == 201

    # Creating a second room with the same name
    second_response = await client.post("/rooms/", headers=headers, json=room_data)
    assert second_response.status_code == 409

# --------- Get room that does not exist ---------#
@pytest.mark.asyncio
async def test_get_one_room_not_found(client):
    headers = await get_token_from_logged_user(client)
    response = await client.get("/rooms/9999", headers=headers)
    assert response.status_code == 404

# --------- Update/Delete room that does not exist ---------#
@pytest.mark.parametrize("method", ["PATCH", "DELETE"])
@pytest.mark.asyncio
async def test_modify_room_not_found(client, method):
    headers = await get_token_from_logged_user(client)
    # Provide the password body so we pass validation and hit the database search
    dummy_data = {"current_password": "test_password123", "room_name": "new_name"}
    response = await client.request(method, "/rooms/9999", json=dummy_data, headers=headers)
    assert response.status_code == 404

# ---------- Wrong password error for updating room ---------- #
@pytest.mark.asyncio
async def test_update_room_wrong_password_bad_request(client):
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)

    room_update_wrong_password_data = {
        "room_name": "updated_room_name",
        "current_password": "wrong_password"
    }
    response = await client.request("PATCH", f"/rooms/{room_id}", json=room_update_wrong_password_data, headers=headers)
    assert response.status_code == 401

# ---------- Wrong password error for deleting room ---------- #
@pytest.mark.asyncio
async def test_delete_room_wrong_password_bad_request(client):
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)

    room_delete_wrong_password_data = {
        "current_password": "wrong_password"
    }
    response = await client.patch(f"/rooms/{room_id}", json=room_delete_wrong_password_data, headers=headers)
    assert response.status_code == 401

# ------ Not authorized user trying to delete or update the room ------- #
@pytest.mark.parametrize("method", ["PATCH", "DELETE"])
@pytest.mark.asyncio
async def test_update_and_delete_room_not_owner_forbidden(client, method):
    room_id = await get_room_id(client)

    header_user_b = await get_token_from_logged_user(client, username="user_b")
    password_data = {"current_password": "hacker_password", "room_name": "hacker_room_name"}

    response = await client.request(method, f"/rooms/{room_id}", json=password_data, headers=header_user_b)
    assert response.status_code == 403

# ---------- Invalid room ID format error for DELETE, PATCH (text instead of number) ---------- #
@pytest.mark.parametrize("method",["PATCH", "DELETE"])
@pytest.mark.asyncio
async def test_delete_update_one_room_invalid_id_unprocessable(client, method):
    headers = await get_token_from_logged_user(client)
    room_id = "invalid_room_id"
    user_data = {"current_password": "password123", "room_name": "new_room_name"}
    response = await client.request(method, f"/rooms/{room_id}", json=user_data, headers=headers)
    assert response.status_code == 422

# ---------- Invalid room ID format error for GET (text instead of number) ---------- #
@pytest.mark.asyncio
async def test_get_one_room_invalid_id_unprocessable(client):
    headers = await get_token_from_logged_user(client)
    room_id = "invalid_room_id"
    response = await client.get(f"/rooms/{room_id}", headers=headers)
    assert response.status_code == 422

# ---------- Invalid pagination test (negative skip value) ---------- #
@pytest.mark.asyncio
async def test_get_all_rooms_invalid_pagination_unprocessable(client):
    headers = await get_token_from_logged_user(client)
    response = await client.get(f"/rooms/?skip=-5", headers=headers)
    assert response.status_code == 422

# ---------- Pagination limit cap test (coerces giant limit) ---------- #
@pytest.mark.asyncio
async def test_get_all_rooms_limit_exceeded_coerced(client):
    headers = await get_token_from_logged_user(client)
    response = await client.get(f"/rooms/?limit=5000000", headers=headers)
    assert response.status_code == 200


