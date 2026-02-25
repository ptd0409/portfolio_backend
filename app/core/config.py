from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    APP_NAME: str = "portfolio"
    APP_ENV: str = "local"
    DEBUG: bool = False
    DATABASE_URL_ASYNC: str
    DATABASE_URL_SYNC: str
    JWT_SECRET_KEY: str = "lwxSl-Nvc3pO7lRzznrBV9qf9aiHs4Q4yKSIpftttUBsEehDytLHECpA7GbK8BVHNYmPxts9MhAONXvWqIxcaQ"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
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
    
settings = Settings()