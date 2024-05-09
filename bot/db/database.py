# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from bot.config.config import settings
from config.config import settings
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logger.info(f"DB url: {settings.db.url}")
engine = create_async_engine(url=settings.db.url, echo=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
