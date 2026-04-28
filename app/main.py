import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api import auth, conversations, messages, websocket
from app.middleware.rate_limit import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAG engine...")
    try:
        from app.ai.rag import get_rag_engine
        get_rag_engine()
        logger.info("RAG engine ready")
    except Exception:
        logger.exception("RAG engine initialization failed — RAG will be unavailable")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="AI Conversational Support Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Credentials + wildcard origin is invalid in browsers; enumerate local dev origins.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."},
    )


app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(websocket.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
