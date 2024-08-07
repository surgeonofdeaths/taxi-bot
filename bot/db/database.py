from config.config import settings
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logger.info(f"DB url: {settings.db.url}")
engine = create_async_engine(url=settings.db.url, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
