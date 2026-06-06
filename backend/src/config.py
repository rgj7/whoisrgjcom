from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: Environment = Environment.PROD
    CORS_ORIGINS: list[str] = []
    GCS_BUCKET_NAME: str = ""
    MEDIA_PUBLIC_BASE_URL: str = ""
    MEDIA_MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024
    MEDIA_MAX_WIDTH: int = 1600

    model_config = SettingsConfigDict(extra="ignore")


settings = Config()  # type: ignore
