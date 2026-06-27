# Global imports
import time
import pytest
from fastapi import status

# Local imports
from tests.test_helper import get_sender_id, get_room_id



# ---------- Message rate limiting tests --------- #

# --------- HAPPY TESTS/SAD TESTS: Testing if 5 or fewer messages sent under 10 sec ------- #

@pytest.mark.asyncio
async def test_rate_limiter_allows_five_messages_under_ten_seconds(client):
    payload = {"content": "Hello test message"}

    # Generate valid authentication headers and actual IDs from your app
    auth_data = await get_sender_id(client, username="limiter_user")
    headers = {"Authorization": auth_data["Authorization"]}
    sender_id = auth_data["sender_id"]

    room_id = await get_room_id(client)

    # Construct the correct URL dynamically using the generated IDs
    url = f"/messages/?sender_id={sender_id}&room_id={room_id}"

    # Start the timer right before the loop
    start_time = time.perf_counter()

    # Send exactly 5 requests (including the authorization headers)
    for i in range(5):
        response = await client.post(url, json=payload, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

    # Stop the timer after the loop finishes
    time_taken = time.perf_counter() - start_time

    # Strictly assert that the total time taken was less than 10 seconds
    assert time_taken < 10

    # Sending a 6th request to run into an error
    blocked_response = await client.post(url, json=payload, headers=headers)

    # This proves the system is actively guarding the door
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ------- User rate limiting tests -------- #

# ------ HAPPY and SAD tests for user registration: Can register 3 times under 60 second ------ #
@pytest.mark.asyncio
async def test_signup_rate_limiter_allows_three_requests_under_sixty_seconds(client):
    url = "/users/"

    # Start the timer right before the loop
    start_time = time.perf_counter()

    # Send exactly 3 successful requests
    for i in range(3):
        payload = {
            "username": f"signup_user_{i}",
            "email": f"signup_user_{i}@email.com",
            "password": "test_password123",
            "confirm_password": "test_password123",
            "is_active": True,
        }
        response = await client.post(url, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

    # Stop the timer after the loop finishes
    time_taken = time.perf_counter() - start_time

    # Strictly verify that the rapid requests happened under 60 secs
    assert time_taken < 60

    # Sending a 4th request to run into an error
    fourth_payload = {
        "username": "signup_user_3",
        "email": "signup_user_3@email.com",
        "password": "test_password123",
        "confirm_password": "test_password123",
        "is_active": True,
    }
    blocked_response = await client.post(url, json=fourth_payload)

    # Verify the application actively blocked the request
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked_response.json()["detail"] == "Rate limit exceeded. Slow down!"


# ------ HAPPY and SAD tests for user login: Can register 3 times under 60 second ------ #
@pytest.mark.asyncio
async def test_login_rate_limiter_allows_five_requests_under_sixty_seconds(client):
    url = "/users/login"

    # Start the timer right before the loop
    start_time = time.perf_counter()

    # Send exactly 5 successful requests
    for i in range(5):
        payload = {
            "username": "login_user_1",
            "password": "what_ever_password",
        }
        response = await client.post(url, data=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Stop the timer after the loop finishes
    time_taken = time.perf_counter() - start_time

    # Strictly verify that the rapid requests happened under 60 secs
    assert time_taken < 60

    # Sending a 4th request to run into an error
    sixth_payload = {
            "username": "login_user_1",
            "password": "what_ever_password",
        }
    blocked_response = await client.post(url, data=sixth_payload)

    # Verify the application actively blocked the request
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked_response.json()["detail"] == "Rate limit exceeded. Slow down!"

