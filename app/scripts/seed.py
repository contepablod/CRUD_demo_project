# app/scripts/seed.py
import json
import os
import string
import time
from urllib import error, request
from urllib.parse import urljoin

SEED_N = int(os.getenv("SEED_N", "5"))
SEED_PREFIX = os.getenv("SEED_PREFIX", "Demo")
EXPLICIT_URL = os.getenv("SEED_URL", "").strip()  # optional override

CANDIDATES = [
    "http://localhost:8000/",
    "http://127.0.0.1:8000/",
    "http://api:8000/",  # service name inside docker-compose network
]


def check_health(base: str, timeout: float = 2.5) -> bool:
    try:
        with request.urlopen(urljoin(base, "health"), timeout=timeout) as resp:
            if resp.status != 200:
                return False
            payload = json.loads(resp.read().decode("utf-8") or "{}")
            return bool(payload.get("ok"))
    except Exception:
        return False


def pick_base_url() -> str:
    # If user explicitly provided a URL, prefer it (and trust it).
    if EXPLICIT_URL:
        # If they passed a collection URL (/items/), trim to base.
        if EXPLICIT_URL.rstrip("/").endswith("/items"):
            return EXPLICIT_URL.rsplit("/items", 1)[0] + "/"
        if EXPLICIT_URL.endswith("/items/"):
            return EXPLICIT_URL.rsplit("items/", 1)[0]
        return EXPLICIT_URL if EXPLICIT_URL.endswith("/") else EXPLICIT_URL + "/"

    # Otherwise probe common candidates
    for base in CANDIDATES:
        if check_health(base):
            return base
    # Last resort: return first candidate (may fail but gives a clear error)
    return CANDIDATES[0]


def rand_suffix(k=5) -> str:
    import secrets

    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(k))


def post_item(items_url: str, name: str, description: str):
    data = json.dumps({"name": name, "description": description}).encode("utf-8")
    req = request.Request(
        items_url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body


def main():
    base = pick_base_url()
    items_url = urljoin(base, "items/")
    print(f"Seeding {SEED_N} items to {items_url}")

    ok = 0
    for i in range(SEED_N):
        name = f"{SEED_PREFIX} {i + 1} · {rand_suffix()}"
        desc = f"Seeded item #{i + 1} from Makefile"
        try:
            status, body = post_item(items_url, name, desc)
            if 200 <= status < 300:
                ok += 1
                print(f"  ✓ {name}")
            else:
                print(f"  × {name} (HTTP {status}) {body}")
        except error.HTTPError as e:
            print(f"  × {name} (HTTP {e.code}) {e.read().decode('utf-8', 'ignore')}")
        except Exception as e:
            print(f"  × {name} (error: {e})")
        time.sleep(0.05)
    print(f"Done. Inserted {ok}/{SEED_N}")


if __name__ == "__main__":
    main()
