# Global imports
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

# Local imports
from tests.test_helper import get_token_from_logged_user, get_room_id


# ------ USER MODULE CACHE TESTS ------ #

# --------- CACHE HIT TEST: Checks if second GET request reads from Redis RAM instead of DB ------- #
@pytest.mark.asyncio
async def test_view_profile_reads_from_cache_on_second_request(client):
    # Logging in as new user
    headers = await get_token_from_logged_user(client, username="caching_user_profile")
    url = "/users/me"

    # Making the first request to get inside redis
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # Mock the database service layer to throw an error if the database gets called again
    with patch(
        "app.modules.users.user_service.UserService.check_user_profile",
        new_callable=AsyncMock,
        side_effect=Exception("Database was used instead of the cache!")
    ):
        # Making the second request
        # If it reads from Redis RAM, it passes cleanly.
        second_res = await client.get(url, headers=headers)
        assert second_res.status_code == status.HTTP_200_OK


# --------- INVALIDATION TEST: Checks if PATCH request deletes the old cache from Redis ------- #
@pytest.mark.asyncio
async def test_update_profile_invalidates_existing_cache(client):
    # Logging in as new user
    headers = await get_token_from_logged_user(client, username="caching_user_profile")
    url = "/users/me"

    # Making the first request to get inside redis
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # Updating the details so that cache get deleted
    payload = {
        "username": "a_new_username",
        "current_password": "test_password123",
    }
    second_res = await client.patch(url, headers=headers, json=payload)
    assert second_res.status_code == status.HTTP_200_OK

    # Setting up the trap for redis to go to the real database and to fail
    with patch(
        "app.modules.users.user_service.UserService.check_user_profile",
        new_callable=AsyncMock,
        side_effect=Exception("Cache was cleared successfully!")
    ):
        try:
            # This should cause a Cache Miss and try to hit the DB trap
            await client.get(url, headers=headers)
            pytest.fail("The old cache was not cleared by the DELETE route!")

        except Exception as e:
            # Catching the exception proves the cache was cleared successfully
            assert str(e) == "Cache was cleared successfully!"


# --------- INVALIDATION TEST: Checks if DELETE request deletes the cache from Redis ------- #
@pytest.mark.asyncio
async def test_delete_user_invalidates_existing_cache(client):
    # Logging in as new user
    headers = await get_token_from_logged_user(client, username="caching_user_profile")
    url = "/users/me"

    # Making the first request to get inside redis
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # Deleting the details so that cache get deleted
    payload = {
        "password": "test_password123",
    }
    second_res = await client.request("DELETE", url, headers=headers, json=payload)
    assert second_res.status_code == status.HTTP_200_OK

    # Final request: Since the cache is gone, the app checks the DB,
    # sees the user is missing, and naturally rejects the request with a 401 or 404.
    final_res = await client.get(url, headers=headers)
    assert final_res.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


# ------ ROOM MODULE CACHE TESTS ------ #

# --------- INVALIDATION TEST: Checks if POST request deletes the room list cache from Redis ------- #
@pytest.mark.asyncio
async def test_create_room_invalidates_all_rooms_cache(client):
    # Logging in as a new user
    headers = await get_token_from_logged_user(client, username="create_room_caching")
    url = "/rooms/"

    # Making the first request to get inside redis
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # Creating a new room to delete the old cache
    payload = {
        "room_name": "a_new_room_name"
    }
    second_res = await client.post(url, headers=headers, json=payload)
    assert second_res.status_code == status.HTTP_201_CREATED

    # Setting up the trap for redis to go to the real database and to fail
    with patch(
            "app.modules.rooms.room_service.RoomService.get_all_rooms",
            new_callable=AsyncMock,
            side_effect=Exception("Cache was cleared successfully!")
    ):
        try:
            # This should cause a Cache Miss and try to hit the DB trap
            await client.get(url, headers=headers)
            pytest.fail("The old cache was not cleared by the DELETE route!")

        except Exception as e:
            # Catching the exception proves the cache was cleared successfully
            assert str(e) == "Cache was cleared successfully!"


# --------- STORAGE TEST: Checks if GET request saves the room list to Redis cache ------- #
@pytest.mark.asyncio
async def test_view_all_rooms_saves_to_cache(client):
    # 1. Log in a user
    headers = await get_token_from_logged_user(client, username="cache_user")
    url = "/rooms/"

    # 2. First GET request hits the database and saves the data to Redis cache
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # 3. Set a trap on the database service function to throw an error if hit
    with patch(
        "app.modules.rooms.room_service.RoomService.get_all_rooms",
        new_callable=AsyncMock,
        side_effect=Exception("Database was touched when it shouldn't be!")
    ):
        # 4. Second GET request should read from Redis RAM and ignore the DB completely
        second_res = await client.get(url, headers=headers)

        # 5. Verify that it returned 200 OK cleanly from the cache without hitting our trap
        assert second_res.status_code == status.HTTP_200_OK


# --------- STORAGE TEST: Checks if GET request saves a single room to Redis cache ------- #
@pytest.mark.asyncio
async def test_view_single_room_saves_to_cache(client):
    # Logging in as a new user
    headers = await get_token_from_logged_user(client)

    # Getting the room id
    room_id = await get_room_id(client)
    url = f"/rooms/{room_id}"

    # 3. First GET request hits the database and populates Redis
    first_res = await client.get(url, headers=headers)
    assert first_res.status_code == status.HTTP_200_OK

    # 4. Set a database trap on the service layer method
    with patch(
        "app.modules.rooms.room_service.RoomService.get_room_by_room_id",
        new_callable=AsyncMock,
        side_effect=Exception("Database was touched when it shouldn't be!")
    ):
        # 5. Second GET request must read from Redis and avoid the database
        second_res = await client.get(url, headers=headers)
        assert second_res.status_code == status.HTTP_200_OK
        assert second_res.json()["room_id"] == room_id


# --------- INVALIDATION TEST: Checks if PATCH request deletes both single and list room caches ------- #
@pytest.mark.asyncio
async def test_update_room_invalidates_cache(client):
    # 1. Log in user and create a room
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)

    single_url = f"/rooms/{room_id}"
    list_url = "/rooms/"

    # 2. Prime both caches by making GET requests
    await client.get(single_url, headers=headers)
    await client.get(list_url, headers=headers)

    # 3. Update the room to trigger cache invalidation
    update_data = {
        "room_name": "Updated Room Name",
        "current_password": "test_password123"
    }
    patch_res = await client.patch(single_url, json=update_data, headers=headers)
    assert patch_res.status_code == status.HTTP_200_OK

    # 4. Set a trap on BOTH database get methods
    with patch(
            "app.modules.rooms.room_service.RoomService.get_room_by_room_id",
            new_callable=AsyncMock,
            side_effect=Exception("Single room cache was NOT deleted!")
    ), patch(
        "app.modules.rooms.room_service.RoomService.get_all_rooms",
        new_callable=AsyncMock,
        side_effect=Exception("List rooms cache was NOT deleted!")
    ):
        # 5. Verify single cache was deleted (should hit the trap)
        with pytest.raises(Exception, match="Single room cache was NOT deleted!"):
            await client.get(single_url, headers=headers)

        # 6. Verify list cache was deleted (should hit the trap)
        with pytest.raises(Exception, match="List rooms cache was NOT deleted!"):
            await client.get(list_url, headers=headers)


# --------- INVALIDATION TEST: Checks if DELETE request deletes both single and list room caches ------- #
@pytest.mark.asyncio
async def test_delete_room_invalidates_cache(client):
    # 1. Log in user and create a room
    headers = await get_token_from_logged_user(client)
    room_id = await get_room_id(client)

    single_url = f"/rooms/{room_id}"
    list_url = "/rooms/"

    # 2. Prime both caches by making GET requests
    await client.get(single_url, headers=headers)
    await client.get(list_url, headers=headers)

    # 3. Update the room to trigger cache invalidation
    delete_data = {
        "current_password": "test_password123"
    }
    delete_res = await client.request("DELETE", single_url, json=delete_data, headers=headers)
    assert delete_res.status_code == status.HTTP_200_OK

    # 4. Set a trap on BOTH database get methods
    with patch(
            "app.modules.rooms.room_service.RoomService.get_room_by_room_id",
            new_callable=AsyncMock,
            side_effect=Exception("Single room cache was NOT deleted!")
    ), patch(
        "app.modules.rooms.room_service.RoomService.get_all_rooms",
        new_callable=AsyncMock,
        side_effect=Exception("List rooms cache was NOT deleted!")
    ):
        # 5. Verify single cache was deleted (should hit the trap)
        with pytest.raises(Exception, match="Single room cache was NOT deleted!"):
            await client.get(single_url, headers=headers)

        # 6. Verify list cache was deleted (should hit the trap)
        with pytest.raises(Exception, match="List rooms cache was NOT deleted!"):
            await client.get(list_url, headers=headers)

# ------ MESSAGE MODULE CACHE TESTS ------ #
