from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy import text

from core.config import settings
from api.api_v1.router import api_router
from core.logging import LoggingMiddleware
from db.session import engine

# ─── Rate Limiter ─────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ─── Sentry Observability ─────────────────────
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.2 if settings.is_production else 1.0,
        profiles_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
        release=f"vireoniq@v0.9.0-beta",
        send_default_pii=False,  # GDPR compliance
    )

# ─── Lifespan Context Manager ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite tables & seed if running in SQLite fallback mode
    from db.session import is_sqlite, engine
    if is_sqlite:
        from db.models import Base
        import db.models  # Ensure all models are loaded
        try:
            print("Auto-initializing SQLite tables...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("SQLite tables initialized successfully.")
            
            # Seed default roles and test user
            from scripts.seed_user import seed_user
            await seed_user()
        except Exception as e:
            print(f"Failed to auto-initialize SQLite: {e}")

    # Startup: Initialize Qdrant collections
    try:
        from core.qdrant import qdrant_client as client
        from qdrant_client.http.models import Distance, VectorParams
        
        # Check and create collections
        try:
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if "resume_embeddings" not in collection_names:
                client.recreate_collection(
                    collection_name="resume_embeddings",
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            if "known_answers" not in collection_names:
                client.recreate_collection(
                    collection_name="known_answers",
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            if "psychometric_dna" not in collection_names:
                client.recreate_collection(
                    collection_name="psychometric_dna",
                    vectors_config=VectorParams(size=128, distance=Distance.COSINE)
                )
            print("Successfully initialized Qdrant collections.")
        except Exception as e:
            print(f"Failed to query Qdrant collections: {e}")
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")
        
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="VIREONIQ Career Outcomes Engine API",
    version="0.9.0-beta",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if not settings.is_production else None,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ─── Rate Limiter Registration ────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ─── Global Error Handling ────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "A critical system error occurred. Our engineers have been notified.",
            "path": request.url.path,
            "status": "critical"
        }
    )

# ─── Middleware ───────────────────────────────
# 1. CORS Middleware (Must be first to handle OPTIONS)
if settings.BACKEND_CORS_ORIGINS:
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    # Add common dev origins if not in production
    if not settings.is_production:
        origins.extend(["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"])
        origins = list(set(origins)) # Remove duplicates

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 2. Logging & Error Tracking
app.add_middleware(LoggingMiddleware)

# 3. Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; sandbox;"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

# 4. Trailing Slash Fix (to avoid 307 redirects)
@app.middleware("http")
async def remove_trailing_slash(request, call_next):
    path = request.url.path
    if path != "/" and path.endswith("/"):
        from starlette.responses import RedirectResponse
        return RedirectResponse(url=str(request.url).rstrip("/"))
    return await call_next(request)

# ─── Static Files ────────────────────────────
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─── Routers ─────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)

# ─── Root & Health ───────────────────────────
@app.get("/", tags=["system"])
def root():
    return {
        "service": "VIREONIQ API",
        "version": "0.9.0-beta",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """
    Health check endpoint verifying databases connectivity.
    """
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Healthcheck Database connection error: {e}")
        db_status = "disconnected"
        
    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }
