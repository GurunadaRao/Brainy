import asyncio
from functools import wraps
from typing import Any, Callable

from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.configs.settings import settings

# Create async engine using settings.database_url, disabling pooling for CLI/worker environments
engine = create_async_engine(
    settings.database_url, poolclass=NullPool, echo=settings.DEBUG
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_context() -> AsyncSession:
    """Async context manager provider for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def with_retry(
    max_retries: int = 3, backoff_factor: float = 0.5
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to retry async database operations on connection/operational failures."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except (OperationalError, InterfaceError) as e:
                    retries += 1
                    if retries > max_retries:
                        raise e
                    sleep_time = backoff_factor * (2 ** (retries - 1))
                    print(
                        f"Database connection error: {e}. Retrying {retries}/{max_retries} in {sleep_time}s..."
                    )
                    await asyncio.sleep(sleep_time)
                except Exception as e:
                    raise e

        return wrapper

    return decorator
