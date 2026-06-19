from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from src.configs.settings import settings
from src.api.health import health_router
from src.api.chat import chat_router
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from src.observability.telemetry import registry

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def metrics_endpoint():
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "online",
        "message": "Welcome to Brainy 1.0 Video Intelligence API",
        "environment": settings.APP_ENV
    }
