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

An async backend for a multi-room chat app, built with FastAPI, WebSockets, PostgreSQL, and Redis. Users register, create or join rooms, and exchange messages over a persistent WebSocket connection that's backed by Redis pub/sub so it can run across more than one server process.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Redis · Alembic · JWT · Pytest

---

## Why it's built this way

**Layered architecture (router → service → repository → model).** Routes only handle HTTP/WebSocket concerns and call a service; services hold the business rules; repositories are the only thing that touches the database. This is mostly about testability — services can be unit tested against a mocked repository without spinning up Postgres, and it keeps a route handler from turning into a 100-line function that mixes validation, queries, and response shaping.

**Redis pub/sub instead of broadcasting straight from the WebSocket handler.** The `ConnectionManager` that tracks open WebSocket connections lives in process memory, so it only knows about clients connected to *that* instance. If this API ever ran behind a load balancer with more than one worker, a message sent on instance A would never reach a client connected to instance B. Publishing every message to a Redis channel and having a background task (`live_messages`, started in the app's `lifespan`) consume it and re-broadcast locally solves that — every instance subscribes to the same channel, so it doesn't matter which one a given client landed on.

**JWT over server-side sessions.** No session store to keep in sync across instances; the token carries everything the API needs to verify a request. The trade-off is no built-in revocation — a stolen token works until it expires, which is the main thing I'd address with a refresh-token + denylist setup if this went further.

**Redis for caching and rate limiting, Postgres for everything that needs to survive a restart.** Message history is cached for 5 minutes per room and invalidated on write. Per-user rate limiting (5 requests / 10 seconds) is applied to both sending a message over the WebSocket and the REST `POST /messages` endpoint, using a Redis counter with a TTL.

---

## Project structure

```
app/
├── main.py                 # app setup, middleware, lifespan (starts the Redis listener)
├── redis_client.py         # background task: consumes the Redis channel, persists + broadcasts
├── core/
│   ├── config.py            # settings from environment variables
│   ├── database.py          # async SQLAlchemy engine/session
│   └── security.py          # password hashing, JWT creation
├── api/
│   └── dependencies.py      # auth dependency, rate limiter, cache helpers, service injection
├── modules/
│   ├── users/                # register, login, profile
│   ├── rooms/                 # create/update/delete/list rooms
│   └── messages/              # REST message history + the WebSocket endpoint
└── utils/                    # shared validation helpers

tests/                        # ~1,800 lines covering auth, rooms, messages, caching,
                               # rate limiting, the WebSocket flow, and the Redis worker
alembic/                      # database migrations
```

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

# optional — only needed if you want the welcome email on signup
GMAIL_USER=
GMAIL_APP_PASSWORD=
```

Then apply migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The API is at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

To run Redis (and the app itself) in Docker instead:

```bash
docker compose up --build
```

The compose file only containerizes Redis and the app — Postgres is expected to be running on the host (connected via `host.docker.internal`).

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
- `GET /?room_id=` — recent messages for a room (cached, paginated via `limit`)
- `POST /?room_id=` — send a message over REST
- `WS /messages/ws/{room_id}?token=` — live connection; send plain text, receive every message broadcast to that room

All routes except register/login require a `Bearer` token from `/users/login`. The WebSocket takes the same JWT as a query parameter, since the WebSocket handshake doesn't carry custom headers the way a normal request does.

---

## Testing

```bash
pytest -v
```

Tests run against a separate test database and use `fakeredis` to avoid needing a real Redis instance, so the suite is self-contained. Coverage includes the auth flow, rate limiting behavior, cache hit/miss/invalidation, the WebSocket connect/send/disconnect cycle, and the background Redis worker that persists and rebroadcasts messages.

---

## Known limitations / what I'd do next

- **No token revocation.** A logout or password change doesn't invalidate already-issued tokens. The next step would be to refresh tokens with a denylist in Redis.
- **Cache invalidation is a wildcard `KEYS` delete**, which is fine at this scale but blocks Redis on a large keyspace. `SCAN` is the production-correct version.
- **Rate limiter's increment-then-expire isn't atomic** — a process crash between the two Redis calls could leave a counter without a TTL. A small Lua script would close that gap.
- **No read receipts, presence, or message editing/deletion** — the schema and service layer were left open enough to add these without restructuring, but they're not built.
- **Horizontal scaling is solved for fan-out (via Redis pub/sub) but not yet load-tested** — I haven't pushed this past a handful of concurrent connections locally.

---

## Author

**Sagnik Santra**
