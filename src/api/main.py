from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.chat import chat_router
from src.api.health import health_router
from src.configs.settings import settings
from src.observability.telemetry import registry

# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT]
)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure Security Middlewares
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "host.docker.internal"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


# Enable OpenTelemetry Instrumentation
FastAPIInstrumentor.instrument_app(app)


@app.get("/metrics")
async def metrics_endpoint() -> Response:
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "online",
        "message": "Welcome to Brainy 1.0 Video Intelligence API",
        "environment": settings.APP_ENV,
    }
