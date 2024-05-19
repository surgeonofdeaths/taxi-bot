import os
import subprocess

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


class Settings(BaseSettings):
    bot: BotSettings
    logging: Logging
    db: DatabaseSettings
    helpcrunch: HelpcrunchSettings


print(subprocess.run(["ls", "-la", "bot/config"]))
print(os.getcwd())

settings: Settings = Settings.parse_file(
    path="bot/config/config.json",
    encoding="utf-8",
)
url = (
    f"postgresql+{settings.db.drivername}://"
    f"{settings.db.user}:{settings.db.password}@"
    f"{settings.db.host}:{settings.db.port}"
    f"/{settings.db.database}"
)
settings.db.url = url
