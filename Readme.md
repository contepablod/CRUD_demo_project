# FastAPI Async CRUD – Postgres + SQLAlchemy + Docker

A production‑ready, async CRUD API with a small HTML landing page. It uses **FastAPI**, **SQLAlchemy 2.x (async)**, **PostgreSQL**, **Alembic** for migrations, and ships with **Docker** (dev + prod), a **Makefile** for DX, **pytest** tests, and a hardened **pre-commit** suite (ruff, mypy, detect‑secrets, commitizen).

> **Highlights**
> - Async service layer & repository pattern
> - HTML page at `/` with a tiny dashboard + live health badge
> - Fully containerized (dev hot-reload, prod slim image)
> - Seed data from JSON or random items
> - CI-friendly, typed, linted, secret-scanned

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Local Development](#local-development)
- [Running with Docker](#running-with-docker)
- [Makefile Commands](#makefile-commands)
- [Environment Variables](#environment-variables)
- [Database & Migrations](#database--migrations)
- [Seeding Data](#seeding-data)
- [API Endpoints](#api-endpoints)
- [HTML Landing](#html-landing)
- [Testing](#testing)
- [Pre-commit & Commit Style](#pre-commit--commit-style)
- [Secret Scanning](#secret-scanning)


---

## Architecture

```
.
├── app
│   ├── main.py                      # FastAPI app (lifespan: init models, shutdown); middleware; CORS; HTML route
│   ├── api/
│   │   └── items.py                 # /items CRUD endpoints (uses service via Depends)
│   ├── services/
│   │   └── items.py                 # Business logic (ItemService)
│   ├── persistence/
│   │   └── repositories.py          # SqlAlchemyItemRepository (async)
│   ├── db/
│   │   └── connection.py            # Async engine, session_scope, healthcheck, init_models
│   ├── domain/
│   │   └── models.py                # SQLAlchemy Declarative Base + Item model
│   ├── schemas/
│   │   └── item.py                  # Pydantic models (Create / Update / Out)
│   ├── templates/
│   │   └── index.html               # HTML landing w/ simple UI
│   ├── scripts/
│   │   └── seed.py                  # In-container seeder (random items)
│   └── tests/
│       ├── conf_test.py             # Test settings (LifespanManager etc.)
│       └── test_items.py            # End-to-end CRUD test via httpx
├── alembic.ini
├── migrations/                      # Alembic env + versions/
├── docker-compose.yaml              # Dev stack (hot reload, bind mount)
├── docker-compose.prod.yml          # Prod stack (optimized image)
├── dockerfile                       # Multi-stage (builder + slim runtime)
├── makefile                         # DX helpers
├── .pre-commit-config.yaml          # Lint/format/type/tests/secrets on commit/push
├── .secrets.baseline                # detect-secrets baseline (tracked)
├── .env.example                     # Template env vars (no secrets)
├── pyproject.toml                   # Pin deps (ruff, mypy, etc.)
├── mypy.ini / pytest.ini            # Tooling config
└── README.md
```

---

## Tech Stack

- **FastAPI** (async ASGI) + **Uvicorn**
- **SQLAlchemy 2.x async** + **asyncpg** (Postgres)
- **Alembic** migrations
- **Jinja2** templates for the landing page
- **pytest**, **httpx**, **asgi-lifespan** for async tests
- **ruff**, **ruff-format**, **mypy**, **pyupgrade**
- **pre-commit**, **commitizen**, **detect-secrets**
- **Docker** (multi-stage), **docker-compose**

---

## Local Development

```bash
# 1) Create a virtualenv and install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) Set environment (copy template)
cp .env.example .env
# edit DATABASE_URL if you want local Postgres, otherwise you can run via Docker

# 3) Run API locally (needs DB up and DATABASE_URL configured)
uvicorn app.main:app --reload --port 8000

# Open http://localhost:8000/  (HTML) or http://localhost:8000/docs (Swagger)
```

> If running Postgres locally, ensure the user/db exist and match your `DATABASE_URL`.

---

## Running with Docker

### Dev (hot reload, bind mount)
```bash
make dev         # equivalent to MODE=dev make up (uses docker-compose.yaml)
```

### Prod (optimized image, no bind)
```bash
make prod        # equivalent to MODE=prod make up (uses docker-compose.prod.yml)
```

Common:
```bash
make up          # start stack (foreground)
make down        # stop stack
make logs        # tail API logs
make build       # build images
make prune       # stop & remove containers + volumes (⚠ destroys dev DB)
```

---

## Makefile Commands

| Target            | What it does |
|-------------------|--------------|
| `make dev`        | Start dev stack (hot reload, bind mount) |
| `make prod`       | Start prod stack (optimized multi-stage image) |
| `make up`         | `docker compose up` with mode-aware files |
| `make down`       | Stop containers |
| `make logs`       | Tail API logs |
| `make build`      | Build images |
| `make rebuild`    | Build images without cache |
| `make ps`         | List services |
| `make sh`         | Shell into API container |
| `make restart`    | Restart API container |
| `make prune`      | Stop & remove containers + volumes |
| `make health`     | Host health check (`GET /health`) |
| `make shealth`    | In-container health check |
| `make wait`       | Wait until API is healthy |
| `make dbwait`     | Wait until Postgres is ready |
| `make revision`   | Create Alembic migration (`M="message"`) |
| `make migrate`    | Apply latest migrations |
| `make downgrade`  | Roll back one migration |
| `make seed`       | Seed N demo items **from inside** the API container |
| `make seedcurl`   | Seed N items **from host** using curl |
| `make seedfile`   | Seed items from JSON file (default `app/data/seeds.json`) |
| `make test`       | Run test suite |
| `make lint`/`fmt` | Ruff lint / format |
| `make type`       | mypy type check |
| `make secret-scan`| detect-secrets scan (and optional gitleaks) |

> Many targets are **mode-aware** via `MODE=dev|prod` and use the right compose file(s).

---

## Environment Variables

Configure via `.env` (example provided in `.env.example`).

- `DATABASE_URL` — async SQLAlchemy URL.

**Notes**
- For **SQLite** (quick local runs/tests): `sqlite+aiosqlite:///./test.db`
- In **Docker**, the compose files set this to the internal `db` host for you.

---

## Database & Migrations

We use **Alembic** to manage schema changes.

```bash
# Create a new migration (autogenerate)
make revision M="add items table"

# Apply latest migrations
make migrate

# Roll back one step
make downgrade
```

> The app’s lifespan (in `main.py`) also runs `Base.metadata.create_all` on startup, which is handy for ephemeral/local/dev. In real prod, favor **explicit Alembic migrations**.

---

## Seeding Data

There are three ways to seed demo data:

1) **Inside the container** (script reads env vars):
```bash
make seed
# variables you can override:
#   SEED_N=20 SEED_PREFIX=Foo SEED_URL=http://localhost:8000/items/
```

2) **From the host using curl** (random N items):
```bash
make seedcurl SEED_COUNT=10 SEED_PREFIX="Demo" SEED_BASE="http://localhost:8000/"
```

3) **From a JSON file** (array of `{name, description}`):
```bash
# default path: app/data/seeds.json
make seedfile SEED_FILE=app/data/seeds.json SEED_BASE="http://localhost:8000/"
```

> `make seedcurl` / `seedfile` can be run against **any** reachable base URL via `SEED_BASE`.

---

## API Endpoints

- `GET /health` → `{"ok": true}` if DB is reachable
- `GET /items/` → list items (query: `limit`, `offset`, `q`)
- `GET /items/{id}` → get single item
- `POST /items/` → create item
- `PATCH /items/{id}` → partial update
- `DELETE /items/{id}` → delete

### cURL Examples

```bash
# Create (note trailing slash)
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test item","description":"Hello from Ubuntu"}'

# List
curl http://127.0.0.1:8000/items/?limit=10

# Get
curl http://127.0.0.1:8000/items/<id>

# Update
curl -X PATCH http://127.0.0.1:8000/items/<id> \
  -H "Content-Type: application/json" \
  -d '{"description":"updated"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/items/<id> -i
```

> `POST /items` (without slash) returns `307` redirect to `/items/`. Either follow redirects or always include the trailing `/` when creating.

---

## HTML Landing

- `GET /` serves `app/templates/index.html` (Jinja2).
- It shows:
  - Service title + health badge (queries `/health`)
  - Quick cURL copy button
  - Create form (POSTs to `/items/`)
  - A small table with the latest items (`GET /items/?limit=50`)

You can edit the page and the embedded JS to improve styling/UX.

> In VS Code, hit **Ctrl+Shift+V** (or `Cmd+Shift+V`) to preview `README.md`.

---

## Testing

We use **pytest** + **httpx** + **asgi-lifespan** to run the app in‑process with lifespan events.

```bash
# In a venv:
make test
# or directly:
PYTHONPATH=. pytest -q --maxfail=1
```

**Notes**
- Tests can run on **SQLite** by setting `DATABASE_URL=sqlite+aiosqlite:///./test.db`.
- For Postgres tests, ensure a running DB and a valid `DATABASE_URL` (and create the test DB).

---

## Pre-commit & Commit Style

Install hooks (once):
```bash
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

What runs:
- **pre-commit**: trailing whitespace, end-of-file-fixer, check-yaml/toml, pyupgrade, ruff (lint + format), detect-secrets
- **pre-push**: `mypy` + quick `pytest` (configurable)
- **commit-msg**: **commitizen** (conventional commits)

Example commit:
```
feat(api): add search filter to list items
```

---

## Secret Scanning

We track a **detect-secrets** baseline and ship a convenience target:

```bash
make secret-scan
```

- If `gitleaks` is installed, it’s also invoked as an extra layer.
- Never commit real secrets. Use `.env.example` placeholders like `CHANGE_ME` and keep `.env` out of Git.

---

## License

MIT (or your preferred license)
