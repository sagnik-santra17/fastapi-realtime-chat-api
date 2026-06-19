#Global imports
import logging
import time
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

app = FastAPI(title="Chat-room API")

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