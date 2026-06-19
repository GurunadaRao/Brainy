import asyncpg
import pika
import requests
from fastapi import APIRouter
from minio import Minio
from neo4j import AsyncGraphDatabase

from src.configs.settings import settings

health_router = APIRouter()


async def _check_postgres() -> str:
    try:
        conn = await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))
        await conn.close()
        return "up"
    except Exception as e:
        return f"error: {str(e)}"


async def _check_neo4j() -> str:
    try:
        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        async with driver:
            await driver.verify_connectivity()
        return "up"
    except Exception as e:
        return f"error: {str(e)}"


def _check_qdrant() -> str:
    try:
        url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/readyz"
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            return "up"
        else:
            return f"status: {res.status_code}"
    except Exception as e:
        return f"error: {str(e)}"


def _check_rabbitmq() -> str:
    try:
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1,
            )
        )
        connection.close()
        return "up"
    except Exception as e:
        return f"error: {str(e)}"


def _check_minio() -> str:
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        minio_client.list_buckets()
        return "up"
    except Exception as e:
        return f"error: {str(e)}"


@health_router.get("/health")
async def health_check() -> dict:
    postgres_status = await _check_postgres()
    neo4j_status = await _check_neo4j()
    qdrant_status = _check_qdrant()
    rabbitmq_status = _check_rabbitmq()
    minio_status = _check_minio()

    services = {
        "postgres": postgres_status,
        "neo4j": neo4j_status,
        "qdrant": qdrant_status,
        "rabbitmq": rabbitmq_status,
        "minio": minio_status,
    }

    is_degraded = any(status != "up" for status in services.values())

    return {
        "status": "degraded" if is_degraded else "healthy",
        "services": services,
    }
