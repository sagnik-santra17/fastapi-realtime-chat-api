<div align="center">

# ⚡ Real-Time Chat API

### A production-inspired, asynchronous backend built with **FastAPI**, **WebSockets**, **PostgreSQL**, and **Redis**, designed for scalable, secure, and real-time communication.

<p align="center">
A modern backend architecture demonstrating clean software engineering principles, asynchronous programming, layered application design, authentication, caching, and real-time messaging.
</p>

---

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-success?style=for-the-badge&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Cache-critical?style=for-the-badge&logo=redis)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-black?style=for-the-badge)
![WebSocket](https://img.shields.io/badge/WebSocket-RealTime-green?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-Tested-blueviolet?style=for-the-badge&logo=pytest)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

</div>

---

# Real-Time Chat API

An async backend for a multi-room chat app, built with FastAPI, WebSockets, PostgreSQL, and Redis. Users register, create or join rooms, and exchange messages over a persistent WebSocket connection.

This was a personal project to learn how a real backend is structured beyond basic CRUD — async programming, authentication, caching, and real-time communication with WebSockets.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Redis · Alembic · JWT · Pytest

---

## What it does

- Users can register and log in (JWT-based auth, passwords hashed with bcrypt)
- Users can create chat rooms and view/update/delete the ones they own
- Inside a room, users connect over a WebSocket and send/receive messages live
- Message history is stored in PostgreSQL and cached in Redis for faster repeat reads
- Basic rate limiting stops one user from spamming messages

---

## How it's structured

I split the app into layers instead of putting everything in the route functions:

```
Router    → handles the HTTP/WebSocket request itself
Service   → the actual logic (e.g., "can this user delete this room?")
Repository → the only place that talks to the database
Model     → the database table definition
```

The main reason I did it this way: it's much easier to test. A service can be tested by giving it a fake repository instead of needing a real database running, and a route function stays short because it just calls a service and returns the result.

```
app/
├── main.py                 # app setup, middleware
├── redis_client.py         # background task that listens for new messages and broadcasts them
├── core/                   # config, database connection, JWT/password logic
├── api/dependencies.py     # auth check, rate limiter, cache helpers
├── modules/
│   ├── users/                # register, login, profile
│   ├── rooms/                 # create/update/delete/list rooms
│   └── messages/              # message history + the WebSocket endpoint
└── utils/                    # shared validation helpers

tests/                        # tests for auth, rooms, messages, caching, rate limiting, websockets
alembic/                      # database migrations
```

---

## Why Redis is in here, not just Postgres

This is the part I'm most proud of figuring out. WebSocket connections are tracked in memory while the server is running — there's a dictionary mapping each chat room to the list of users currently connected to it. That works fine for one server.

But if this app ever ran on two servers at once (which is normal for handling more traffic), each server would only know about *its own* connected users. A message sent on Server 1 would never reach a user connected to Server 2.

To fix that, instead of broadcasting a message directly, the WebSocket handler publishes it to a Redis channel. A background task (started when the app starts up) listens to that channel, saves the message to Postgres, and then broadcasts it to whichever users are connected to *that* server. Every server runs this same background task and listens to the same channel, so it doesn't matter which server a user happens to be connected to — they all hear everything published.

Redis is also used for two smaller things: caching the last 50 messages of a room for 5 minutes (so repeated requests don't hit Postgres every time), and counting how many messages a user has sent recently for rate limiting.

---

## Running it locally

**Prerequisites:** Python 3.13+, PostgreSQL, Redis (or just use Docker for Redis).

```bash
git clone <repo-url>
cd real_time_chat_api

python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/chat_db
SECRET_KEY=replace-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379

# optional — only needed for the welcome email on signup
GMAIL_USER=
GMAIL_APP_PASSWORD=
```

Apply migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

To run Redis (and the app) in Docker instead:

```bash
docker compose up --build
```

The compose file containerizes Redis, and the app — Postgres is expected to already be running on the host machine.

---

## API overview

**Users** (`/users`)
- `POST /` — register
- `POST /login` — returns a JWT
- `GET /me`, `PATCH /me`, `DELETE /me` — current user profile

**Rooms** (`/rooms`)
- `POST /` — create a room
- `GET /`, `GET /{room_id}` — list/view rooms
- `PATCH /{room_id}`, `DELETE /{room_id}` — update or delete (room creator only)

**Messages** (`/messages`)
- `GET /?room_id=` — recent messages for a room (cached)
- `POST /?room_id=` — send a message over REST
- `WS /messages/ws/{room_id}?token=` — live connection; send plain text, receive every message broadcast to that room

All routes except register/login require a `Bearer` token from `/users/login`. The WebSocket takes the same JWT as a query parameter instead of a header, since the WebSocket handshake doesn't let the browser attach custom headers.

---

## Testing

```bash
pytest -v
```

Tests use a separate test database and `fakeredis`, so you don't need a real Redis instance running just to run the suite. They cover the auth flow, rate limiting, cache behavior, the WebSocket connect/send/disconnect cycle, and the background worker that saves and rebroadcasts messages.

---

## What I'd improve with more time

- **Logging out doesn't actually invalidate a token.** Since JWTs are just verified, not looked up anywhere, a token keeps working until it naturally expires (30 min by default), even after "logout." A proper fix needs a way to track revoked tokens server-side.
- **Cache invalidation uses Redis's `KEYS` command with a wildcard**, which scans every key in Redis to find matches. Fine for this project's size, but on a much bigger dataset it would briefly block all other Redis operations. `SCAN` does the same job in smaller, non-blocking chunks.
- **The rate limiter increments a counter and sets its expiry as two separate Redis commands**, not one atomic step. If the app crashed in between those two calls, that counter could be left without an expiry and never reset. I'd want to combine those into a single script-based command.
- **No presence, typing indicators, or read receipts** — the layered structure should make these easier to add later without rewriting things, but they're not built yet.

---

## Author

**Sagnik Santra**
