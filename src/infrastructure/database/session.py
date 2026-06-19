from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from src.configs.settings import settings

# Create async engine using settings.database_url, disabling pooling for CLI/worker environments
engine = create_async_engine(settings.database_url, poolclass=NullPool, echo=settings.DEBUG)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
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
