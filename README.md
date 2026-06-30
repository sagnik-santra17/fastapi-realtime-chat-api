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

# 📖 Overview

**Real-Time Chat API** is a scalable backend application built with modern Python technologies to demonstrate production-oriented backend development.

The project goes beyond traditional CRUD operations by implementing asynchronous request handling, JWT authentication, WebSocket communication, Redis caching, background processing, repository-service architecture, and comprehensive automated testing.

The primary goal of this project is to showcase software engineering best practices while maintaining clean, maintainable, and extensible code.

---

# ✨ Key Features

## Authentication & Security

- JWT-based authentication
- Secure password hashing using Passlib/Bcrypt
- Protected API endpoints
- Request validation with Pydantic
- Centralized authentication dependencies
- Security middleware
- Environment-based configuration

---

## Real-Time Communication

- Native FastAPI WebSocket support
- Multi-user chat rooms
- Connection manager
- Persistent messaging
- Async communication
- Connection lifecycle management

---

## Backend Architecture

- Layered architecture
- Repository Pattern
- Service Layer
- Modular application structure
- Dependency Injection
- Async SQLAlchemy ORM
- Centralized configuration
- Clean separation of concerns

---

## Database

- PostgreSQL support
- SQLAlchemy 2.0 Async ORM
- Alembic migrations
- Relational data models
- Async database sessions

---

## Performance

- Redis caching
- Async request handling
- Non-blocking database operations
- Optimized dependency injection
- Background workers

---

## Developer Experience

- Docker support
- Automated migrations
- Pytest test suite
- Async test support
- Environment configuration
- Modular project organization

---

# 🏗 System Architecture

```text
                     Client Applications
      ┌────────────────────────────────────────┐
      │                                        │
      │   Browser   Mobile App   API Client    │
      │                                        │
      └────────────────────────────────────────┘
                       │
                       ▼
               FastAPI Application
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Authentication    REST API     WebSocket
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 Service Layer
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Repository      Redis Cache    Background Tasks
        │
        ▼
 SQLAlchemy Async ORM
        │
        ▼
   PostgreSQL Database
```

---

# 🏛 Application Design

The project follows a layered architecture to keep business logic isolated from infrastructure.

```text
              API Routers
                   │
                   ▼
             Service Layer
                   │
                   ▼
          Repository Layer
                   │
                   ▼
         SQLAlchemy Models
                   │
                   ▼
            PostgreSQL Database
```

Each layer has a clearly defined responsibility.

| Layer | Responsibility |
|--------|---------------|
| Router | HTTP endpoints, validation, responses |
| Service | Business rules and application logic |
| Repository | Database interaction |
| Models | Database schema |
| Schemas | Request and response validation |
| Core | Configuration, security, database setup |
| Utils | Helper utilities |

This separation improves maintainability, testing, scalability, and code readability.

---

# 🛠 Technology Stack

| Category | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.13 | Primary programming language |
| Framework | FastAPI | High-performance asynchronous API framework |
| ORM | SQLAlchemy 2.0 | Async ORM and database abstraction |
| Database | PostgreSQL | Persistent relational storage |
| Cache | Redis | High-speed caching and message handling |
| Authentication | JWT | Stateless authentication |
| Password Security | Passlib + Bcrypt | Password hashing |
| Validation | Pydantic v2 | Request/response validation |
| Migration | Alembic | Database schema versioning |
| Testing | Pytest | Automated testing |
| Async Testing | pytest-asyncio | Async endpoint testing |
| HTTP Client | HTTPX | Integration testing |
| Containerization | Docker | Local development and deployment |

---

# 🎯 Engineering Highlights

This project demonstrates practical backend engineering concepts rather than focusing solely on feature implementation.

### ✔ Asynchronous Programming

- Async database sessions
- Async API endpoints
- Async WebSockets
- Non-blocking I/O

---

### ✔ Clean Architecture

- Repository Pattern
- Service Layer
- Dependency Injection
- Modular package organization

---

### ✔ Production-Oriented Development

- Environment-based configuration
- Dockerized development
- Database migrations
- Secure authentication
- Redis integration
- Automated testing

---

### ✔ Scalability Considerations

The application is designed so that additional modules can be introduced with minimal changes to existing components.

Examples include:

- Notifications
- Friend system
- File sharing
- Group administration
- Message reactions
- Read receipts
- Presence tracking

without requiring major architectural changes.

---

# 🚀 Why This Project?

This project was built to demonstrate practical backend software engineering skills, including:

- Designing maintainable APIs
- Building asynchronous systems
- Implementing secure authentication
- Working with relational databases
- Managing application state using Redis
- Structuring large FastAPI applications
- Writing testable and modular code
- Following production-inspired engineering practices

Rather than being a simple CRUD application, this project reflects how modern backend services are commonly structured in real-world software systems.

## 📂 Project Structure

```text
real-time-chat-api/
│
├── alembic/                    # Database migration scripts
├── app/
│   ├── api/                    # API route definitions
│   ├── core/                   # Application configuration, security, middleware
│   ├── database/               # Database session and connection management
│   ├── models/                 # SQLAlchemy ORM models
│   ├── repositories/           # Data access layer
│   ├── schemas/                # Pydantic request & response schemas
│   ├── services/               # Business logic layer
│   ├── websocket/              # WebSocket connection handling
│   ├── workers/                # Background workers
│   ├── utils/                  # Shared helper utilities
│   └── main.py                 # FastAPI application entry point
│
├── tests/                      # Automated test suite
├── docker/                     # Docker configuration (if applicable)
├── .env.example                # Environment variable template
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Multi-container development setup
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

> **Note:** The exact directory names may vary slightly depending on the latest repository structure, but the project follows a modular, feature-oriented architecture with clear separation of responsibilities.

---

# ⚙️ Getting Started

## Prerequisites

Ensure the following software is installed before running the project:

| Software            | Recommended Version |
| ------------------- | ------------------- |
| Python              | 3.13+               |
| PostgreSQL          | 16+                 |
| Redis               | Latest Stable       |
| Docker *(Optional)* | Latest              |
| Git                 | Latest              |

---

## Clone the Repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git

cd <repository-name>
```

---

## Create a Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example configuration:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chat_db

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379

EMAIL_USERNAME=example@email.com

EMAIL_PASSWORD=your-email-password
```

> Never commit your `.env` file or sensitive credentials to version control.

---

# 🐳 Running with Docker

If Docker is configured in the repository:

```bash
docker compose up --build
```

To run in detached mode:

```bash
docker compose up -d
```

Stop the containers:

```bash
docker compose down
```

---

# 🗄 Database Setup

Apply all database migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Describe your changes"
```

---

# ▶️ Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📚 Interactive API Documentation

Once the application is running:

| Documentation | URL                           |
| ------------- | ----------------------------- |
| Swagger UI    | `http://127.0.0.1:8000/docs`  |
| ReDoc         | `http://127.0.0.1:8000/redoc` |

FastAPI automatically generates interactive API documentation based on your route definitions and Pydantic schemas.

---

# 🚦 Common Development Commands

| Task                     | Command                                        |
| ------------------------ | ---------------------------------------------- |
| Start development server | `uvicorn app.main:app --reload`                |
| Apply migrations         | `alembic upgrade head`                         |
| Generate migration       | `alembic revision --autogenerate -m "message"` |
| Run all tests            | `pytest`                                       |
| Run verbose tests        | `pytest -v`                                    |
| Run async tests          | `pytest -v tests/`                             |

---

# 💡 Development Workflow

A typical local development workflow looks like this:

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Configure environment variables.
5. Start PostgreSQL and Redis (or use Docker).
6. Apply database migrations.
7. Launch the FastAPI server.
8. Access the interactive API documentation via Swagger UI.
9. Develop, test, and iterate using the provided test suite.

# 🧪 Testing Strategy

The project includes a comprehensive automated testing suite to ensure reliability, maintainability, and confidence during future development.

The test suite validates both business logic and application behavior across multiple layers of the backend.

## Testing Approach

* Unit tests for service and utility functions
* API endpoint testing using FastAPI's testing utilities
* Asynchronous test execution with `pytest-asyncio`
* Database isolation using a dedicated test database
* Authentication flow validation
* Redis cache verification
* Rate-limiting behavior tests
* Security middleware validation
* WebSocket communication tests

By isolating components and testing them independently, the project minimizes regressions while keeping development iterations fast.

---

# 🔐 Authentication & Authorization

Authentication is implemented using **JSON Web Tokens (JWT)**.

The authentication workflow follows a stateless design, allowing the API to scale horizontally without relying on server-side sessions.

## Authentication Flow

```text id="vwjlwm"
        User Login
             │
             ▼
    Verify Credentials
             │
             ▼
      Generate JWT Token
             │
             ▼
 Client Stores Access Token
             │
             ▼
 Authorization Header
Bearer <access_token>
             │
             ▼
 Protected Endpoints
             │
             ▼
 Token Validation
             │
             ▼
Authorized Request
```

### Security Features

* Password hashing with **Passlib + Bcrypt**
* JWT-based authentication
* Protected routes using FastAPI dependencies
* Environment-based secret management
* Input validation using Pydantic
* Centralized authentication logic
* Stateless authentication architecture

---

# ⚡ Real-Time Messaging

One of the core features of the application is real-time communication through **WebSockets**.

Unlike traditional HTTP requests, WebSockets maintain a persistent connection between the client and server, allowing messages to be delivered instantly.

## Message Flow

```text id="l0rhm7"
Client A
   │
   ▼
WebSocket Endpoint
   │
   ▼
Connection Manager
   │
   ▼
Chat Service
   │
   ▼
Database Persistence
   │
   ▼
Broadcast Message
   │
   ▼
Connected Clients
```

This architecture enables efficient bi-directional communication while keeping connection management isolated from business logic.

---

# 🚀 Redis Integration

Redis is used to improve performance and support scalable real-time functionality.

Depending on the feature, Redis provides:

* High-speed caching
* Temporary data storage
* Pub/Sub messaging
* Background task support
* Reduced database load

Using Redis allows frequently accessed information to be served significantly faster than repeatedly querying the database.

---

# 🗄 Database Design

The application uses **PostgreSQL** together with **SQLAlchemy 2.0 Async ORM**.

The data layer follows the Repository Pattern, separating database interactions from business logic.

```text id="jlvowb"
API Request
      │
      ▼
Service Layer
      │
      ▼
Repository
      │
      ▼
SQLAlchemy ORM
      │
      ▼
 PostgreSQL
```

This abstraction improves:

* Testability
* Maintainability
* Readability
* Future scalability

---

# 🧩 Dependency Injection

FastAPI's dependency injection system is used extensively throughout the application.

Dependencies are responsible for providing:

* Database sessions
* Current authenticated user
* Authentication checks
* Shared configuration
* Request-scoped resources

Using dependency injection keeps route handlers concise while promoting reusable, loosely coupled components.

---

# 🛡 Security Practices

Security was considered throughout the application's design.

Implemented measures include:

* JWT authentication
* Secure password hashing
* Environment variable management
* Request validation
* SQL injection protection through SQLAlchemy ORM
* Strong schema validation with Pydantic
* Authentication middleware
* Security headers
* Protected API routes
* Centralized exception handling

These practices align with common backend security recommendations for modern web APIs.

---

# 💎 Software Engineering Best Practices

The project emphasizes maintainability and clean architecture over tightly coupled implementations.

### Separation of Concerns

Each layer has a single responsibility.

* Routers handle HTTP requests.
* Services implement business logic.
* Repositories manage database operations.
* Schemas validate incoming and outgoing data.
* Models define persistent entities.

---

### Asynchronous Programming

The backend is built around Python's asynchronous ecosystem.

Benefits include:

* Improved concurrency
* Better scalability
* Efficient database communication
* Non-blocking I/O
* Higher throughput under load

---

### Modular Architecture

Features are organized into dedicated modules, making the project easier to navigate and extend.

Adding new functionality typically requires minimal modification to existing code.

---

### Configuration Management

Application settings are managed through environment variables and centralized configuration classes.

This approach keeps sensitive information out of source control while supporting multiple deployment environments.

---

### Database Migrations

Schema evolution is handled through Alembic.

Benefits include:

* Version-controlled database changes
* Reproducible deployments
* Team collaboration
* Reliable schema upgrades

---

### API Validation

All incoming requests and outgoing responses are validated using Pydantic.

This ensures:

* Strong typing
* Consistent API contracts
* Automatic documentation
* Reduced runtime errors

---

# 📈 Performance Considerations

Several architectural decisions improve the overall performance of the application.

* Fully asynchronous request handling
* Connection pooling
* Redis caching
* Stateless authentication
* Optimized dependency injection
* Efficient ORM queries
* Background processing
* Persistent WebSocket connections

These patterns help the application remain responsive while supporting concurrent users.

---

# 🌱 Future Improvements

The architecture has been intentionally designed to support future enhancements with minimal structural changes.

Potential additions include:

* Refresh token rotation
* OAuth2 authentication
* Role-based access control (RBAC)
* End-to-end encrypted messaging
* File and media sharing
* Message reactions
* Read receipts
* User presence indicators
* Push notifications
* Horizontal scaling with Redis Pub/Sub
* Kubernetes deployment
* CI/CD pipeline integration
* Observability with Prometheus and Grafana

---

# 🎯 Project Goals

This project was developed to demonstrate practical backend engineering skills through a production-inspired application.

Key areas of focus include:

* Asynchronous API development
* Real-time communication
* Authentication and security
* Database design
* Clean architecture
* Automated testing
* Scalable application structure
* Modern Python backend development

Rather than focusing solely on implementing features, the project emphasizes writing maintainable, extensible, and production-ready code following industry best practices.


# 🤔 Architecture Decisions

Software architecture is not only about selecting technologies—it's about making informed trade-offs that balance maintainability, scalability, performance, and developer experience.

The architectural decisions in this project were made to closely resemble patterns commonly used in modern backend systems.

---

## Why FastAPI?

FastAPI was chosen because it combines excellent developer ergonomics with high performance.

Its asynchronous foundation enables efficient handling of concurrent requests, while automatic request validation, dependency injection, and interactive API documentation significantly reduce boilerplate code.

These capabilities allow developers to focus on business logic rather than framework-specific implementation details.

---

## Why Asynchronous Programming?

Traditional synchronous applications allocate one thread per request, which can become inefficient when handling I/O-bound operations such as database queries or network communication.

This project adopts Python's asynchronous programming model using `async` and `await` to ensure the application remains responsive while waiting for external resources.

This approach is particularly beneficial for:

* WebSocket communication
* Database operations
* Redis interactions
* High-concurrency workloads

---

## Why PostgreSQL?

PostgreSQL was selected as the primary relational database because of its reliability, consistency, and strong SQL compliance.

It provides robust transactional guarantees, excellent indexing capabilities, and mature tooling, making it a solid choice for applications where data integrity is critical.

Using SQLAlchemy's asynchronous ORM enables efficient interaction with PostgreSQL while maintaining a clean object-oriented programming model.

---

## Why Redis?

Redis complements PostgreSQL by handling workloads where extremely low latency is important.

Instead of querying the database for every operation, Redis provides an in-memory data store suitable for:

* Frequently accessed data
* Temporary application state
* Publish/Subscribe messaging
* Background processing
* Session-like information

Separating these responsibilities allows PostgreSQL to focus on durable data storage while Redis handles high-speed operations.

---

## Why the Repository Pattern?

Directly embedding database queries inside API routes tightly couples business logic to persistence logic, making the codebase harder to test and maintain.

The Repository Pattern introduces a dedicated data access layer that encapsulates all database operations.

This abstraction provides several benefits:

* Easier unit testing through dependency mocking
* Improved maintainability
* Reduced code duplication
* Flexibility to change persistence implementations without affecting business logic

---

## Why a Service Layer?

Business rules evolve more frequently than infrastructure code.

The Service Layer centralizes business logic, ensuring that API routes remain lightweight and focused solely on request handling.

This separation improves readability while allowing multiple interfaces—such as REST APIs, WebSockets, or background workers—to reuse the same business logic without duplication.

---

## Why Dependency Injection?

FastAPI's dependency injection system promotes loosely coupled components by providing shared resources only when required.

Dependencies such as database sessions, authentication handlers, and configuration objects are injected automatically, reducing repetitive code and improving modularity.

This design simplifies testing, as dependencies can be replaced with mock implementations during automated tests.

---

## Why Pydantic?

Reliable APIs require strict validation of incoming and outgoing data.

Pydantic provides type-safe schemas that validate requests before they reach the application's business logic.

Benefits include:

* Automatic input validation
* Consistent response models
* Improved developer experience
* Automatic OpenAPI documentation generation
* Reduced runtime errors

---

## Why Alembic?

Managing database schema changes manually becomes increasingly difficult as applications grow.

Alembic provides version-controlled database migrations, enabling schema changes to be tracked alongside application code.

This ensures that development, testing, and production environments remain synchronized throughout the software lifecycle.

---

## Why Docker?

Containerization provides a consistent execution environment regardless of the host operating system.

By packaging the application together with its dependencies, Docker eliminates "works on my machine" issues and simplifies onboarding for new developers.

It also provides a foundation for future deployment to container orchestration platforms.

---

# 📈 Scalability Considerations

Although this project is intended as a portfolio application, the architecture has been designed with scalability in mind.

Several design decisions support future growth:

* Stateless JWT authentication
* Modular application structure
* Repository abstraction
* Service-oriented business logic
* Asynchronous request handling
* Redis integration
* Database migrations
* Dependency injection
* Environment-based configuration

These choices reduce coupling between components, making the system easier to extend as new requirements emerge.

---

# 🎓 Key Learning Outcomes

This project provided practical experience with several important backend engineering concepts, including:

* Designing layered application architectures
* Building asynchronous APIs with FastAPI
* Implementing secure authentication workflows
* Structuring maintainable service and repository layers
* Managing relational databases using SQLAlchemy
* Version-controlling database schemas with Alembic
* Integrating Redis for caching and real-time functionality
* Developing and testing WebSocket communication
* Writing automated tests for asynchronous applications
* Following production-inspired software engineering practices

---

# 🤝 Contributing

Contributions, feature requests, and constructive feedback are always welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes using meaningful commit messages.
4. Ensure all tests pass.
5. Submit a pull request for review.

Please follow the existing project structure and coding conventions to maintain consistency across the codebase.

---

# 👨‍💻 Author

**Sagnik Santra**

Backend Developer focused on building scalable, asynchronous, and production-inspired applications using modern Python technologies.

If you found this project interesting or have suggestions for improvement, feel free to open an issue or connect with me.

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

Thank you for taking the time to explore this project.

</div>

