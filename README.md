<div align="center">

# ⚡ Real-Time Chat

### A full-stack chat app where people can sign up, join rooms, and talk live.

**[👉 Try it live here 👈](https://fastapi-realtime-chat-api.onrender.com/static/index.html)**

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
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

</div>

---

## 👋 Quick note on how this was built

I'm a **backend developer**, and I want to be upfront about who did what.

- **I hand-wrote the entire backend**: the API, the database, Redis, the live WebSocket chat, and the CI/CD pipeline.
- **AI (Windsurf / Claude) generated the frontend** (the HTML, CSS, and JavaScript you see on screen). I wanted to spend my time on how the system is designed and how fast and reliable the backend is, not on picking button colors.

So if you're here to judge my work, look at the backend. The pretty screen is there so the backend has something to show off.

---

## 🔗 Try it live

**https://fastapi-realtime-chat-api.onrender.com/static/index.html**

The easiest way to see it work:

1. Open the link in a normal browser window.
2. Open it again in an **incognito window** (or a different browser).
3. Create two different accounts, one in each window.
4. Join the same room and start chatting. Messages show up instantly on both sides.

> 💤 It's on a free hosting plan, so if nobody has visited in a while, the first load can take a little while to wake up. Give it a minute.

---

## 💬 What is this?

It's a chat app, a bit like a tiny Slack or Discord. You make an account, hop into a chat room (or make your own), and talk to other people in real time, with no refreshing the page.

Here's what you can do in the app:

- **Sign up and log in** from a simple login screen
- **Browse chat rooms** in a sidebar
- **Chat live** in a room, with messages appearing the second someone sends them
- **Create, edit, and delete your own rooms**
- **Manage your profile**: update your details or delete your account
- **Hang out in ⭐ General Chat ⭐**, a pinned room that stays at the top of the list for everybody

It's dark-mode, and buttons show a little spinner while they're working, so it feels like a real app and not a school project.

---

## 🧰 What it's made of

| Part | What I used |
|------|-------------|
| Backend | Python, FastAPI, WebSockets |
| Frontend | Plain HTML / CSS / JavaScript (AI-generated) |
| Database | PostgreSQL (hosted on Neon) |
| Caching and background worker | Redis (hosted on Render) |
| DevOps | Docker, GitHub Actions (CI/CD), Render |

The backend serves the frontend directly from a `/static` folder. That means there's just one thing to run, with no separate website to set up.

---

## 🤖 The automatic checks and deploy (CI/CD)

This is the part I'm proudest of on the DevOps side.

Every time I push code to GitHub, a little robot (GitHub Actions) does this for me:

1. Spins up a temporary database
2. Runs all **82 tests**
3. Checks that the Docker image builds properly
4. **Only if everything passes**, automatically deploys the new version to Render

If anything fails, nothing goes live. That means I can't accidentally ship something broken.

---

## 📮 How messages travel (and why Redis is here)

When you send a message, it doesn't go straight to the other person. Instead:

1. Your message goes to a **background worker** (powered by Redis) first.
2. The worker **saves the message** in the real database.
3. Then it **broadcasts the message live** to everyone in the room.

Why bother with the extra step? Imagine the app gets popular and I need to run it on two servers instead of one. Without this setup, someone on Server 1 would never see messages from someone on Server 2, because each server only knows about its own users. With the background worker, every server hears every message, so everyone sees everything no matter which server they landed on.

Redis also does two smaller jobs:

- **Remembers the last 50 messages** of a room for 5 minutes, so the database isn't asked the same question over and over
- **Counts how many messages you've sent recently**, so nobody can spam a room

---

## 🏗️ How the code is organized

I split the backend into layers instead of cramming everything into one place. Think of it like a restaurant:

```
Router     → the waiter (takes the request)
Service    → the chef (does the real thinking, like "is this person allowed to delete this room?")
Repository → the pantry (the only part that touches the database)
Model      → the labels on the shelves (what the database tables look like)
```

The big win is that it's much easier to test. I can check the "chef" without needing a real "pantry" running.

```
app/
├── main.py                 # starts the app
├── redis_client.py         # the background worker that saves and broadcasts messages
├── core/                   # settings, database connection, login/password logic
├── api/dependencies.py     # login checks, spam limiter, cache helpers
├── modules/
│   ├── users/              # sign up, log in, profile
│   ├── rooms/              # create, edit, delete, list rooms
│   └── messages/           # message history + the live chat connection
├── static/                 # the frontend (HTML/CSS/JS)
└── utils/                  # small shared helpers

tests/                      # all the tests
alembic/                    # database change history
```

---

## 💻 Running it on your own computer

**Test login:** `test@test.com` / `password123`

**You'll need:** Python 3.13+, PostgreSQL, and Redis (Docker is the easy way to get Redis).

**1. Get the code and install things**

```bash
git clone <repo-url>
cd real_time_chat_api

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**2. Create a `.env` file** in the project's main folder:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/chat_db
SECRET_KEY=replace-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379

# optional, only needed for the welcome email on signup
GMAIL_USER=
GMAIL_APP_PASSWORD=
```

**3. Set up the database and start the server**

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

**4. Open the app** 🎉

Once the server is running, go to:

👉 **http://127.0.0.1:8000/static/index.html**

(If you're curious about the behind-the-scenes API, there's a built-in page at `http://127.0.0.1:8000/docs`.)

**Prefer Docker?**

```bash
docker compose up --build
```

This runs Redis and the app for you. PostgreSQL still needs to be running on your own machine.

---

## 🧪 Running the tests

```bash
pytest -v
```

The tests use a separate test database and a pretend Redis, so you don't need a real Redis running. They cover logging in, spam protection, the caching, the live chat connection, and the background worker.

---

## 🛠️ What I'd improve with more time

- **Logging out doesn't instantly kill your login.** Right now, a login "pass" (a token) keeps working until it naturally runs out, which is 30 minutes by default, even after you hit logout. Think of it like a concert wristband: the venue can't cancel it remotely, it just expires. Fixing this means keeping a "banned wristbands" list on the server.
- **Clearing the cache is a bit clumsy.** To clean out old cached messages, the app asks Redis to search through *every* thing it has stored (the `KEYS` command). That's fine at this size, but in a much bigger app it would make Redis pause for a moment while it searches. There's a gentler way (`SCAN`) that does the same search in small bites.
- **Fancier chat features aren't built yet**, like seeing who's online, "someone is typing…", or read receipts. The way the code is organized should make adding them fairly painless.

---

## 👤 Author

**Sagnik Santra**, Backend Developer
