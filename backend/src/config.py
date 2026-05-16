from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: str
    SITE_DOMAIN: str = "whoisrgj.com"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://blog.whoisrgj.com"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Config()  # type: ignore
