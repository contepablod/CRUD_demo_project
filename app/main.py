import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.api.items import router as items_router
from app.db.connection import healthcheck, init_models, shutdown
from app.domain.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_models(Base)
    yield
    # shutdown
    await shutdown()


app = FastAPI(title="CRUD API (Python)", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    ok = await healthcheck()
    return JSONResponse(status_code=200 if ok else 503, content={"ok": ok})


templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(items_router)

logger = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def add_request_id(request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    logger.info("rid=%s %s %s %s", rid, request.method, request.url.path, response.status_code)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    body = await request.body()
    if len(body) > 1_000_000:  # ~1MB
        return JSONResponse(status_code=413, content={"detail": "Payload too large"})
    request._body = body  # reuse parsed body
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exc_handler(_, exc: Exception):
    # TODO: send to Sentry/Logs
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
