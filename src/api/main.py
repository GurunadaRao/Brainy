import os
import urllib.parse as urlparse
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select

from src.api.chat import chat_router
from src.api.health import health_router
from src.configs.settings import settings
from src.domain.models import Video
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.queue.rabbitmq_client import rabbitmq_client
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


class IngestRequest(BaseModel):
    url: str


def extract_youtube_video_id(url: str) -> str | None:
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse.urlparse(url)
    if parsed_url.hostname in ("youtu.be", "www.youtu.be"):
        return parsed_url.path[1:]
    if parsed_url.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed_url.path == "/watch":
            p = urlparse.parse_qs(parsed_url.query)
            return p.get("v", [None])[0]
        if parsed_url.path.startswith(("/embed/", "/v/")):
            return parsed_url.path.split("/")[2]
    return None


@app.post("/api/v1/ingest")
async def ingest_video(request: IngestRequest) -> dict:
    video_id = extract_youtube_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if video already exists
            stmt = select(Video).where(Video.id == video_id)
            result = await session.execute(stmt)
            existing_video = result.scalar_one_or_none()
            if existing_video:
                if existing_video.status == "failed":
                    existing_video.status = "queued"
                else:
                    return {
                        "video_id": video_id,
                        "status": existing_video.status,
                        "message": "Video already exists",
                    }
            else:
                # Create video entry
                db_video = Video(id=video_id, url=request.url, status="queued")
                session.add(db_video)

    # Publish to RabbitMQ
    rabbitmq_client.publish(
        "video_ingestion", {"url": request.url, "video_id": video_id}
    )
    return {
        "video_id": video_id,
        "status": "queued",
        "message": "Ingestion task successfully queued",
    }


@app.get("/api/v1/videos")
async def get_videos() -> list[dict]:
    async with AsyncSessionLocal() as session:
        stmt = select(Video).order_by(Video.created_at.desc())
        result = await session.execute(stmt)
        videos = result.scalars().all()
        return [
            {
                "id": v.id,
                "url": v.url,
                "title": v.title,
                "duration": v.duration,
                "status": v.status,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in videos
        ]


# Enable OpenTelemetry Instrumentation
FastAPIInstrumentor.instrument_app(app)


@app.get("/metrics")
async def metrics_endpoint() -> Response:
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Index.html not found</h1>", status_code=404)
