from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str
    admin_ids: list[str]
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


class Settings(BaseSettings):
    bot: BotSettings
    logging: Logging
    db: DatabaseSettings


config: Settings = Settings.parse_file(
    path="bot/config/config.json",
    encoding="utf-8",
)
