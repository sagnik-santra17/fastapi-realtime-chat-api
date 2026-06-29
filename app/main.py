#Global imports
import asyncio
import logging
import time
import json
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
#local imports
from app.modules.rooms.room_router import router as room_router
from app.modules.users.user_router import router as user_router
from app.modules.messages.message_router import router as message_router
from app.modules.users.user_model import User
from app.modules.rooms.room_model import Room
from app.modules.messages.message_model import Message
from app.redis_client import live_messages

#-----------logging setup-----------#
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("passlib").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.info("Application starting up...")

# ------ # This creates the "startup checklist" for your server (Redis) ----- #
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Start the endless loop in the background
    task = asyncio.create_task(live_messages())
    yield
    # Stop the loop safely when the server turns off
    task.cancel()

app = FastAPI(title="Chat-room API", lifespan=lifespan)

#---------middleware----------#
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # This rule allows the app to load Swagger files from external CDNs safely
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com;"
    )

    return response

#--------global exception handler---------#
#This catches all HTTP errors, logs 401s, and returns the response
@app.exception_handler(HTTPException)
async def global_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        logger.warning(
            f"Security Warning: Unauthorized {request.method} access attempt to path '{request.url.path}'. "
            f"Reason: {exc.detail}"
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

#--------main app routes---------#
app.include_router(user_router)
app.include_router(room_router)
app.include_router(message_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Chat-room API"}

"""# -------- Test Redis publisher -------- #
@app.get("/test_publish")
async def test_publish():
    # 1. Connecting to local redis server
    redis = aioredis.from_url("redis://localhost:6379", decode_responses=True, protocol=2)

    fake_chat = {
        "user_id": 5,
        "room_id": 14,
        "text": "Hello World!",
    }
    json_str = json.dumps(fake_chat)

    # 2. Publishing the test
    await redis.publish("room:messages", json_str)

    #3. Close the connection
    await  redis.aclose()
    return {"status": "JSON Message sent successfully!"}"""