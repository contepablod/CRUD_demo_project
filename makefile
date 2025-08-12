SHELL := /bin/bash
.ONESHELL:

# Mode-aware docker compose helper
MODE ?= dev

# ---- Seeding defaults ----
SEED_N       ?= 8
SEED_PREFIX  ?= Demo
SEED_URL     ?= http://localhost:8000/items/
SEED_FILE    ?= app/data/seeds.json
SEED_BASE    ?= http://localhost:8000/# host-side curl base
SEED_COUNT   ?= 8                           # used by seedcurl

# Compose files
ifeq ($(MODE),prod)
  COMPOSE := docker compose -f docker-compose.yaml -f docker-compose.yaml
else
  COMPOSE := docker compose -f docker-compose.yaml
endif

APP        ?= api
CURL       ?= curl -sf
HEALTH_URL ?= http://localhost:8000/health
ALEMBIC    ?= $(COMPOSE) exec $(APP) alembic

.PHONY: dev prod up down build rebuild logs ps sh restart prune help \
        health shealth wait dbwait revision migrate downgrade \
        seed reseed seedcurl seedfile

## Seed demo data into the API (override with: SEED_N=20 SEED_PREFIX=Foo)
seed:
	$(MAKE) wait
	$(COMPOSE) exec -T $(APP) sh -lc 'SEED_N=$(SEED_N) SEED_PREFIX="$(SEED_PREFIX)" SEED_URL="$(SEED_URL)" python app/scripts/seed.py'

## Wipe DB volumes (dev) and seed fresh
reseed:
	$(COMPOSE) down -v
	$(MAKE) up &
	$(MAKE) wait
	$(MAKE) seed

## Seed N random items from the host using curl (override: SEED_COUNT=20 SEED_PREFIX=Foo)
seedcurl:
	$(MAKE) wait HEALTH_URL=$(SEED_BASE)health
	@echo "Seeding $(SEED_COUNT) items to $(SEED_BASE)items/ ..."
	i=1
	while [ $$i -le $(SEED_COUNT) ]; do
	  SUF=$$(date +%s%N | tail -c 6)
	  NAME="$(SEED_PREFIX) $$i · $$SUF"
	  DESC="Seeded via seedcurl target"
	  curl -sS -X POST "$(SEED_BASE)items/" \
	    -H "Content-Type: application/json" \
	    -d "$$(printf '{"name":"%s","description":"%s"}' "$$NAME" "$$DESC")" >/dev/null \
	    && echo "  ✓ $$NAME" || echo "  × $$NAME"
	  i=$$((i+1))
	done
	@echo "Done."

## Seed items from a JSON file (array of {name, description})
seedfile:
	$(MAKE) wait HEALTH_URL=$(SEED_BASE)health
	@echo "Seeding from $(SEED_FILE) to $(SEED_BASE)items/ ..."
	if command -v jq >/dev/null 2>&1; then
	  jq -c '.[]' "$(SEED_FILE)" | while read -r row; do
	    curl -sS -X POST "$(SEED_BASE)items/" \
	      -H "Content-Type: application/json" \
	      -d "$$row" >/dev/null && echo "  ✓ $$row" || echo "  × $$row"
	  done
	else
	  echo "jq not found; using python3 fallback"
	  python3 - "$(SEED_FILE)" "$(SEED_BASE)" <<-'PY'
	import json, sys, urllib.request
	path, base = sys.argv[1], sys.argv[2]
	with open(path, 'r', encoding='utf-8') as f:
		items = json.load(f)
	if not isinstance(items, list):
		raise SystemExit("JSON must be an array of {name, description} objects")
	for it in items:
		data = json.dumps(it).encode("utf-8")
		req = urllib.request.Request(base + "items/", data=data,
									headers={"Content-Type":"application/json"},
									method="POST")
		with urllib.request.urlopen(req, timeout=5) as resp:
			resp.read()
		print("  ✓", it.get("name"))
	print("Done.")
	PY
	fi
	@echo "Done."

.PHONY: healthprod
healthprod:
	@$(CURL) $${URL:-https://your-domain/health} && echo "  ✅ OK" || (echo "  ❌ FAIL"; exit 1)

.PHONY: test testcov
test:
	PYTHONPATH=.  pytest -q --maxfail=1 

## Run tests with coverage (requires pytest-cov if you want coverage)
testcov:
	PYTHONPATH=.  pytest -q --maxfail=1 --cov=app

## Start DEV stack (hot reload, bind mounts)
dev:
	$(MAKE) MODE=dev up

## Start PROD stack (optimized image, no bind mounts)
prod:
	$(MAKE) MODE=prod up

## Start services (foreground)
up:
	$(COMPOSE) up

## Stop services (keep volumes)
down:
	$(COMPOSE) down

## Build images
build:
	$(COMPOSE) build

## Build images without cache
rebuild:
	$(COMPOSE) build --no-cache

## Tail API logs
logs:
	$(COMPOSE) logs -f $(APP)

## List running services
ps:
	$(COMPOSE) ps

## Shell into API container
sh:
	$(COMPOSE) exec $(APP) sh

## Restart API container
restart:
	$(COMPOSE) restart $(APP)

## Stop & remove containers + volumes (⚠ destroys dev DB data)
prune:
	$(COMPOSE) down -v

## ---- Health & readiness ----

## Health check from the host (expects API exposed on localhost:8000)
health:
	@$(CURL) $(HEALTH_URL) && echo "  ✅ OK" || (echo "  ❌ FAIL"; exit 1)

## Health check from inside the API container (ignores host port mapping)
shealth:
	@$(COMPOSE) exec -T $(APP) sh -lc 'curl -sf http://localhost:8000/health' \
	&& echo "  ✅ OK" || (echo "  ❌ FAIL"; exit 1)

## Wait for API health (timeout ~30s)
wait:
	@echo "Waiting for API at $(HEALTH_URL) ..."
	for i in $$(seq 1 30); do
	  if $(CURL) $(HEALTH_URL) >/dev/null 2>&1; then
	    echo "  ✅ Healthy"; exit 0
	  fi
	  sleep 1
	done
	echo "  ❌ Timed out"; exit 1

## For Postgres: wait until db is ready (requires postgres client inside container)
dbwait:
	@echo "Waiting for Postgres (db service) ..."
	$(COMPOSE) exec -T db sh -lc 'for i in $$(seq 1 30); do pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB -h localhost -p 5432 && exit 0 || sleep 1; done; exit 1' \
	&& echo "  ✅ DB ready" || (echo "  ❌ DB not ready"; exit 1)

## ---- Alembic migrations ----
## Create a new migration (usage: make revision M="add items table")
revision:
ifndef M
	$(error Provide a message: make revision M="your message")
endif
	$(ALEMBIC) revision -m "$(M)" --autogenerate

## Apply latest migrations
migrate:
	$(ALEMBIC) upgrade head

## Roll back one migration
downgrade:
	$(ALEMBIC) downgrade -1

## Show this help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'