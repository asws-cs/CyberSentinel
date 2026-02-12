from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from utils.logger import logger

# The database engine
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# Async session maker
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def get_session() -> AsyncSession:
    """
    Dependency to get a database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def create_db_and_tables():
    """
    Creates all database tables defined by SQLModel metadata.
    """
    async with engine.begin() as conn:
        logger.info("Initializing database and creating tables...")
        # The following import is needed to ensure models are registered with SQLModel
        from database import models
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully.")

async def close_db_connection():
    """
    Closes the database engine connection.
    """
    logger.info("Closing database connection.")
    await engine.dispose()
