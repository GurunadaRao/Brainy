from fastapi import APIRouter
from src.configs.settings import settings
import asyncpg
from neo4j import AsyncGraphDatabase
import requests
import pika
from minio import Minio

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> dict:
    health_status = {
        "status": "healthy",
        "services": {
            "postgres": "down",
            "neo4j": "down",
            "qdrant": "down",
            "rabbitmq": "down",
            "minio": "down"
        }
    }

    # 1. Check PostgreSQL
    try:
        conn = await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))
        await conn.close()
        health_status["services"]["postgres"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["postgres"] = f"error: {str(e)}"

    # 2. Check Neo4j
    try:
        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        async with driver:
            await driver.verify_connectivity()
        health_status["services"]["neo4j"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["neo4j"] = f"error: {str(e)}"

    # 3. Check Qdrant
    try:
        url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/readyz"
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            health_status["services"]["qdrant"] = "up"
        else:
            health_status["status"] = "degraded"
            health_status["services"]["qdrant"] = f"status: {res.status_code}"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["qdrant"] = f"error: {str(e)}"

    # 4. Check RabbitMQ
    try:
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1
            )
        )
        connection.close()
        health_status["services"]["rabbitmq"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["rabbitmq"] = f"error: {str(e)}"

    # 5. Check MinIO
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        # Check if buckets can be listed as a connectivity probe
        minio_client.list_buckets()
        health_status["services"]["minio"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["minio"] = f"error: {str(e)}"

    return health_status
