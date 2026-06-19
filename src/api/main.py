from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.configs.settings import settings
from src.api.health import health_router
from src.api.chat import chat_router

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


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "online",
        "message": "Welcome to Brainy 1.0 Video Intelligence API",
        "environment": settings.APP_ENV
    }
