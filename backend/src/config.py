from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_BASE_URL: str
    DATABASE_NAME: str | None = None
    SITE_DOMAIN: str = "whoisrgj.com"
    ENVIRONMENT: Environment = Environment.PROD

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://blog.whoisrgj.com"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        name = self.DATABASE_NAME or self._derive_db_name()
        return f"{self.DATABASE_BASE_URL}/{name}"

    @property
    def test_database_url(self) -> str:
        return f"{self.DATABASE_BASE_URL}/test_whoisrgj"

    def _derive_db_name(self) -> str:
        match self.ENVIRONMENT:
            case Environment.DEV:
                return "whoisrgj_dev"
            case Environment.PROD:
                return "whoisrgj_prod"
        msg = f"Unknown environment: {self.ENVIRONMENT}"  # type: ignore[unreachable]
        raise ValueError(msg)


settings = Config()  # type: ignore
