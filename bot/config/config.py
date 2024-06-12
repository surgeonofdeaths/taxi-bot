import os

from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str
    admin_ids: list[int]
    parse_mode: str


class Logging(BaseSettings):
    serialize: bool
    sink: str
    rotation: str
    compression: str
    format: str
    level: str


class DatabaseSettings(BaseSettings):
    drivername: str
    user: str
    password: str
    host: str
    port: int
    database: str
    url: str


class HelpcrunchSettings(BaseSettings):
    bearer_token: str
    request_api_wait: int


class Settings(BaseSettings):
    bot: BotSettings
    logging: Logging
    db: DatabaseSettings
    helpcrunch: HelpcrunchSettings


settings: Settings = Settings.parse_file(
    path="bot/config/config.json",
    encoding="utf-8",
)

load_dotenv()
DATABASE_PRIVATE_URL = os.getenv("DATABASE_PRIVATE_URL")
# DATABASE_PRIVATE_URL = "postgresql://postgres:UCaIjjWYVoWcJAHwKHBavuNkrvRHQshg@viaduct.proxy.rlwy.net:28877/railway"

logger.info(DATABASE_PRIVATE_URL)

if DATABASE_PRIVATE_URL:
    logger.info("PROD")
    url = "postgresql+asyncpg" + DATABASE_PRIVATE_URL.lstrip("postgresql")
    logger.info(url)
else:
    logger.info("DEV")
    url = (
        f"postgresql+{settings.db.drivername}://"
        f"{settings.db.user}:{settings.db.password}@"
        f"{settings.db.host}:{settings.db.port}"
        f"/{settings.db.database}"
    )
settings.db.url = url
