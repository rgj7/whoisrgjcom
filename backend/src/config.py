from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: Environment = Environment.PROD
    CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(extra="ignore")


settings = Config()  # type: ignore
