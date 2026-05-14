from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from backend.constants import Environment

class Config(BaseSettings):
    DATABASE_URL: str
    
    SITE_DOMAIN: str = "whoisrgj.com"

    ENVIRONMENT: Environment = Environment.PRODUCTION

    # CORS_ORIGINS: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Config()  # type: ignore

