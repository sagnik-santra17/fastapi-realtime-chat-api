# Global imports
import asyncio
import logging
import redis.asyncio as aioredis
import json

# local imports
from app.core.database import AsyncSessionLocal
from app.modules.messages.message_model import Message
from app.modules.messages.connection_manager import manager

# ---------------------------------------------------------------- #

logger = logging.getLogger(__name__)

async def live_messages():
    # ------- LINE 1 (Listener) ------- #
    listener_redis = aioredis.from_url("redis://localhost:6379", decode_responses=True, protocol=2)
    pubsub = listener_redis.pubsub()
    await pubsub.subscribe("room:messages")

    # ------- LINE 2 (Worker) ------- #
    worker_redis = aioredis.from_url("redis://localhost:6379", decode_responses=True, protocol=2)
    logger.info("Redis: redis is is active...")

    try:
        # ----- Creating a loop to listen/check the incoming messages ----- #
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:

                # 1. Getting the raw text string from Redis
                raw_string = message["data"]

                # 2. Unpacking the raw string to a simple Python Dictionary
                data_dict = json.loads(raw_string)

                # 3. Pulling the specific data pieces
                chat_text = data_dict["text"]
                user_id = data_dict["user_id"]
                room_id = data_dict["room_id"]

                # 4. Using the specific data for logger
                logger.info(f"User {user_id} sent this in room {room_id}: {chat_text}")

                # Opening a manual database door
                async with AsyncSessionLocal() as db:
                    # Creating a new message blueprint object using the SQLAlchemy model
                    new_msg = Message(
                        sender_id=user_id,
                        room_id=room_id,
                        content=chat_text,
                    )
                    db.add(new_msg)
                    await  db.commit()

                    logger.info(f"Successfully saved message to the database!")

                    # This allows WebSocket to instantly show the messages to users' screen
                    await manager.broadcast(room_id=room_id, message=f"User {user_id}: {chat_text}")

                await asyncio.sleep(0.1)

    # Catch any database errors here instead of letting the loop die
    except Exception as e:
        logger.error(f"DATABASE ERROR CAUGHT: {e}")

    finally:
        # Closing both lines safely
        await worker_redis.aclose()
        await listener_redis.aclose()