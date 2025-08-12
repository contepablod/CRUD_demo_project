# 🚀 Python Async CRUD API

A clean, layered **FastAPI** application with a **Connection Service** and **Persistence Layer** for default CRUD operations.
Built with **SQLAlchemy Async** + **Pydantic v2** + **PostgreSQL** (SQLite-ready) and organized for scalability.

---

## 📂 Project Structure

<!-- Write the project structure -->
app/
├─ api/ # HTTP routes
│ └─ items.py
├─ core/ # Config & settings
│ └─ config.py
├─ db/ # DB connection service
│ └─ connection.py
├─ domain/ # ORM models
│ └─ models.py
├─ persistence/ # Repository interface + implementation
│ └─ repositories.py
├─ schemas/ # Pydantic request/response models
│ └─ item.py
├─ services/ # Business logic
│ └─ items.py
└─ main.py # App bootstrap


---

## 🛠️ Tech Stack

- **FastAPI** – high-performance Python web framework
- **SQLAlchemy Async** – async ORM
- **PostgreSQL** (default) – relational database
  *(can be swapped to SQLite for dev/testing)*
- **Pydantic v2** – data validation & serialization
- **Uvicorn** – ASGI server

---

1️⃣ Project Goal

We set out to create a Python-based CRUD API with:

    A clean, layered architecture (Connection Service, Persistence Layer, Service Layer, API Layer)

    Async-first design for performance

    Ready to swap between PostgreSQL (default) and SQLite (quick local)

    A developer-friendly landing page with interactive features

2️⃣ Core Architecture

We used FastAPI for the HTTP layer, SQLAlchemy Async for ORM/database operations, and Pydantic v2 for input/output validation.

The layers are:

    Connection Service

        Manages database engine & sessions

        Provides health checks

        Controls startup/shutdown cleanup

    Persistence Layer

        Repository interface: defines the CRUD contract

        Repository implementation: actual SQLAlchemy queries for items table

    Service Layer

        Business logic

        Calls repositories and enforces rules

    API Layer

        FastAPI routes that:

            Parse/validate requests

            Call the service layer

            Return clean JSON responses

3️⃣ Database

    Default: PostgreSQL connection using asyncpg

    Alternative: SQLite with aiosqlite (no server required)

    Table: items with fields id, name, description, created_at, updated_at

    Auto-creates schema on startup for demo purposes (in production we’d use migrations like Alembic)

4️⃣ CRUD Endpoints

    POST /items/ → create an item

    GET /items/ → list items (with pagination + search)

    GET /items/{id} → fetch one

    PATCH /items/{id} → update one

    DELETE /items/{id} → remove one

    GET /health → DB health check

5️⃣ Landing Page

We built a custom HTML homepage for /:

    Health badge that checks /health

    Links to:

        Swagger UI docs

        ReDoc docs

        Items JSON list

    Curl snippet (copy-to-clipboard) for creating an item

    Browser form to create an item (no curl required)

    A live table showing latest items:

        Refresh button

        Auto-refresh after creation

        Inline editing (name & description)

        Inline deleting with confirmation

This page is fully static HTML/CSS/JS served by FastAPI using Jinja2 (though right now we keep it simple and don’t actually render dynamic server-side data).
6️⃣ Dockerization

We made the app container-friendly:

    Dockerfile: builds a Python image with FastAPI & deps, ready for production

    docker-compose.yml: runs API + Postgres together in dev mode

        Hot reload (mounts your app/ directory)

        Shared network so API talks to DB by service name (db)

    Works equally well in dev (live reload) or prod (frozen image without reload)

7️⃣ Developer Experience

We’ve covered:

    Clear .env config for DB URL & environment

    Code organized into logical modules

    Health checks for readiness probes

    Optional SQLite for quick start

    Landing page for easy onboarding without needing Postman

    Live UI for CRUD without leaving the browser

    Curl commands for CLI fans

    Hot reload in dev

    Ready to add:

        Alembic migrations

        Auth (API keys, JWT)

        CORS for frontend integration

        Logging/metrics

8️⃣ What’s Working Right Now

If you start the API (via Uvicorn locally or docker compose up), you get:

    Fully functional CRUD API

    Swagger docs

    A friendly landing page where you can:

        See health

        Create items

        View all items

        Edit inline

        Delete inline

    Changes instantly saved in the DB
