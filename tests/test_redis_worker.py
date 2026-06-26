# Global imports
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

# Local imports
from app.modules.messages.message_model import Message
from app.redis_client import live_messages
from tests.conftest import TestAsyncSessionLocal

#--------- Happy tests -------- #

# ----------- Testing if the Redis worker saves the messages in database ------- #
@pytest.mark.asyncio
async def test_redis_worker_saves_message(db_session):
    # MagicMock makes .pubsub() act like a normal function, matching real Redis design
    mock_redis = MagicMock()

    # AsyncMock lets us use 'await' on async tools like .subscribe() and .get_message()
    mock_pubsub = AsyncMock()

    # Explicitly makes the close tool awaitable so 'await worker_redis.aclose()' doesn't crash
    mock_redis.aclose = AsyncMock()

    # The test dictionary data structured exactly like a real incoming chat message
    test_data = {
        "text": "Hello Tester",
        "user_id": 1,
        "room_id": 1
    }

    # Redis wraps data inside an 'envelope' containing a message type and raw text string
    redis_message = {
        "type": "message",
        "data": json.dumps(test_data)
    }

    # Feeds the worker data on the 1st turn, then triggers an error to break the infinite loop
    mock_pubsub.get_message.side_effect = [redis_message, GeneratorExit("Stop Loop")]

    # Connects our fake pubsub tools together so the worker uses them
    mock_redis.pubsub.return_value = mock_pubsub

    # Redirects the worker away from live network ports to use our fake connections
    with patch("app.redis_client.aioredis.from_url", return_value=mock_redis), \
            patch("app.redis_client.AsyncSessionLocal", TestAsyncSessionLocal):

        try:
            # Runs the real worker loop so it can catch and process our mock message
            await live_messages()
        except GeneratorExit:
            # Catches our custom loop breaker so the test finishes cleanly instead of crashing
            pass

    # Opens a direct door to the temporary test database to check the hard drive
    async with TestAsyncSessionLocal() as db:
        from sqlalchemy import select

        # Builds a database search query using your SQLAlchemy Message model
        stmt = select(Message).filter_by(content="Hello Tester")
        result = await db.execute(stmt)
        saved_message = result.scalar_one_or_none()

    # Proves the message finished its journey, saved successfully, and mapped to sender_id
    assert saved_message is not None
    assert saved_message.sender_id == 1

# ------------ Sad tests ------------- #

# ----------- Testing if the Redis worker ignores bad data and stays alive ------- #
@pytest.mark.asyncio
async def test_redis_worker_saves_message(db_session):
    mock_redis = MagicMock()
    mock_pubsub = AsyncMock()
    mock_redis.aclose = AsyncMock()

    # Not including the user_id to make it a bad message
    test_data = {
        "text": "Hello Tester",
        "room_id": 1
    }
    redis_message = {
        "type": "message",
        "data": json.dumps(test_data)
    }

    mock_pubsub.get_message.side_effect = [redis_message, GeneratorExit("Stop Loop")]
    mock_redis.pubsub.return_value = mock_pubsub

    with patch("app.redis_client.aioredis.from_url", return_value=mock_redis), \
            patch("app.redis_client.AsyncSessionLocal", TestAsyncSessionLocal):

        try:
            await live_messages()
        except GeneratorExit:
            pass

    async with TestAsyncSessionLocal() as db:
        from sqlalchemy import select
        stmt = select(Message).filter_by(content="Hello Tester")
        result = await db.execute(stmt)
        saved_message = result.scalar_one_or_none()

    # The database should be empty because the worker ignored the bad message
    assert saved_message is None


# ----------- Testing if the Redis worker ignores completely broken text ------- #
@pytest.mark.asyncio
async def test_redis_worker_ignores_malformed_json(db_session):
    mock_redis = MagicMock()
    mock_redis.aclose = AsyncMock()
    mock_pubsub = AsyncMock()

    # Putting fake junk data instead of a structured JSON string
    redis_message = {
        "type": "message",
        "data": "BROKEN_TEXT"
    }

    mock_pubsub.get_message.side_effect = [redis_message, GeneratorExit("Stop Loop")]
    mock_redis.pubsub.return_value = mock_pubsub

    with patch("app.redis_client.aioredis.from_url", return_value=mock_redis), \
            patch("app.redis_client.AsyncSessionLocal", TestAsyncSessionLocal):
        try:
            # Turning on the read worker engine
            await live_messages()
        except GeneratorExit:
            pass

    # Verifying that nothing was saved to the database
    async with TestAsyncSessionLocal() as db:
        from sqlalchemy import select
        stmt = select(Message).filter_by(content="BROKEN_TEXT")
        result = await db.execute(stmt)
        saved_message = result.scalar_one_or_none()

        # The database should be empty because the worker ignored the bad message
        assert saved_message is None

# ----------- Testing if the Redis worker survives a database crash ------- #
@pytest.mark.asyncio
async def test_redis_worker_survives_database_down():
    mock_redis = MagicMock()
    mock_redis.aclose = AsyncMock()
    mock_pubsub = AsyncMock()

    # A perfect message data package
    test_data = {
        "text": "Hello World",
        "room_id": 1,
        "user_id": 99
    }
    redis_message = {
        "type": "message",
        "data": json.dumps(test_data)
    }

    # We expect the worker to check Redis TWICE: once for the message, once for the stop signal
    mock_pubsub.get_message.side_effect = [redis_message, GeneratorExit("Stop Loop")]
    mock_redis.pubsub.return_value = mock_pubsub

    # Building a fake database session that triggers when .commit() is called
    mock_db_session = AsyncMock()
    mock_db_session.commit.side_effect = Exception("Database is completely OFFLINE!")

    # Configuring a fake factory to hand this broken session to the worker
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_db_session

    # Redirect the worker to use our fake Redis and our broken Database factory
    with patch("app.redis_client.aioredis.from_url", return_value=mock_redis), \
         patch("app.redis_client.AsyncSessionLocal", mock_session_factory):
        try:
            await live_messages()
        except GeneratorExit:
            pass

    # A count of 2 proves the worker loop survived the database crash and stayed alive to look for the next message.
    assert mock_pubsub.get_message.call_count == 2