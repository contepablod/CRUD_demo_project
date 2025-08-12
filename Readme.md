# CRUD API — FastAPI + Postgres + Docker + Pre-commit

A production-ready Python web service demonstrating clean architecture, PostgreSQL persistence, full CRUD operations, and modern development workflows.

This project includes:
    ⚡ FastAPI for a blazing-fast REST API with async support

    🗄 PostgreSQL database with SQLAlchemy 2.x ORM

    🔄 Full Create, Read, Update, Delete (CRUD) endpoints

    📦 Docker for both development and production

    🔥 Hot-reload dev mode, optimized multi-stage production build

    🧪 pytest async testing with HTTPX & lifespan handling

    🧹 pre-commit hooks for code hygiene, commit message rules, and secret scanning

    🛡 Security checks for accidental secret commits

    📜 Built-in example HTML UI to interact with the API

## 📂 Project Structure

app/
├── api/                # API routes (FastAPI routers)
│   └── items.py        # CRUD endpoints for 'items'
├── db/                 # Database connection and session utilities
│   └── connection.py
├── domain/             # Database models and domain entities
│   └── models.py
├── templates/          # Jinja2 HTML templates (frontend UI)
├── tests/              # Pytest-based async test suite
│   └── test_items.py
├── main.py              # FastAPI application entrypoint
├── scripts/            # Optional seeding/migration scripts
data/
└── seeds.json          # Example seed data
docker-compose.yaml     # Dev stack
docker-compose.prod.yml # Prod stack
Dockerfile              # Multi-stage build
Makefile                # CLI commands for dev/prod/test/deploy
.pre-commit-config.yaml # Hooks for lint/format/security

## 🚀 Features

    Async database operations via SQLAlchemy + asyncpg

    Postgres persistence with automatic migrations (Alembic)

    JSON + HTML rendering (API + simple frontend)

    Request logging with unique request IDs

    CORS support

    Payload size limiting middleware

    Error handling for unexpected exceptions

    Health check endpoint (/health)

    Seed data loaders (from JSON or generated)

## 🛠 Requirements

    Python 3.12+

    Docker & Docker Compose v2

    make (for Makefile tasks)

    Node not required — frontend uses plain HTML + JS

## 📦 Setup

Clone the repo:

`git clone https://github.com/yourusername/crud-api.git`
`cd crud-api`

Create a virtual environment (for local dev):

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

## 🐳 Running the stack

We use a mode-aware Makefile so you can instantly switch between dev and prod workflows.

### Dev mode (hot reload, bind mounts)
`make dev`

    Mounts source code into container

    Auto-reloads on code changes

    Postgres runs in a container

    API runs at http://localhost:8000

### Prod mode (optimized build)

`make prod`

    Multi-stage Docker build (smaller image)

    No bind mounts

    Suitable for deployment

### 🗂 API Endpoints

Method	Path	Description

GET	/health	Health check

GET	/items/	List items

POST	/items/	Create new item

GET	/items/{id}	Get item by ID

PATCH	/items/{id}	Update item

DELETE	/items/{id}	Delete item

Example:

`curl -X POST http://localhost:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test item", "description": "Hello world"}'`


## 🌱 Seeding the database

From host:

`make seedfile SEED_FILE=app/data/seeds.json`

From generated data:

`make seedcurl SEED_COUNT=10 SEED_PREFIX="Demo"`

## 🧪 Running tests

Tests are async and use FastAPI’s ASGI lifespan.

`make test`
or
`PYTHONPATH=. pytest -q`

## 🧹 Code quality & commit rules

We use pre-commit hooks to ensure all code is clean before it’s committed:

    Ruff — linting + formatting

    pyupgrade — auto-modernize Python syntax

    mypy — optional type checks (on push)

    Commitizen — enforce Conventional Commits

    detect-secrets / gitleaks — prevent secret leaks

Install hooks:

`pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg`

Run all hooks manually:

`pre-commit run -a`

## Secret scanning

    detect-secrets: baseline file .secrets.baseline tracks known false positives.

To scan manually:

`make secret-scan`

## 🖥 Frontend UI

Visit http://localhost:8000 in your browser to:

    View health status

    Create items via form

    View item list

    See live updates without reloading

## 🧭 Development flow

Start stack:

`make dev`

Code changes — Hot reload applies instantly.

Run tests:

`make test`

Stage changes:

`git add .`

Commit with prompts:

`cz commit`

Push to repo:

`git push`

## 🛡 Production deployment

Ensure MODE=prod

Build & run optimized image:

`make prod`

Set DATABASE_URL to production Postgres

Place behind a reverse proxy (e.g., Nginx, Caddy) with HTTPS

Configure allow_origins in main.py for your frontend domain

## 📝 License

MIT License — feel free to use and adapt.
