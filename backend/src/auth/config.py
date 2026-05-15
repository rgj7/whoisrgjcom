
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXP_MINUTES: int = 60


auth_settings = AuthConfig()  # type: ignore
