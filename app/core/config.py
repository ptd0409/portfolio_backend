from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "portfolio"
    APP_ENV: str = "production"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DEBUG: bool = False
    DATABASE_URL_ASYNC: str
    DATABASE_URL_SYNC: str
    ADMIN_API_KEY: str = Field(default="change-me")
    JWT_SECRET_KEY: str = "ccab9952550af26a081446f35b5f479a3047e169e6c473603c00df5f42142384"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str]
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_USE_TLS: bool = True
    SMTP_FROM_NAME: str = "Portfolio Admin"

    FRONTEND_URL: str
    VERIFY_EMAIL_TOKEN_EXPIRE_MINUTES: int = 60

    CONTACT_RECEIVER_EMAIL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # Helpers
    @property
    def cors_list(self) -> list[str]:
        if not self.CORS_ORIGINS.strip():
            return []
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]
    
    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str):
        allowed = {"local", "dev", "staging", "prod"}
        if v not in allowed:
            raise ValueError(f"Value must be one of {allowed}")
        return v
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
settings = Settings()