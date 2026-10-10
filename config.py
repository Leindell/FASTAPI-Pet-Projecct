"""Все настройки в одном месте. Значения берутся из переменных окружения CRYPTID_*."""
import os

from pydantic import BaseModel, Field

DEFAULT_SECRET = "dev-secret-change-me"


class Settings(BaseModel):
    db: str = "cryptid.db"
    secret: str = DEFAULT_SECRET
    token_minutes: int = Field(default=30, gt=0)
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"


def load_settings(environ: dict[str, str] = os.environ) -> Settings:
    """CRYPTID_TOKEN_MINUTES=60 -> token_minutes=60. Pydantic сам приведёт "60" к int и проверит."""
    values: dict = {
        key.removeprefix("CRYPTID_").lower(): value
        for key, value in environ.items()
        if key.startswith("CRYPTID_")
    }
    if "cors_origins" in values:
        values["cors_origins"] = values["cors_origins"].split(",")
    return Settings(**values)


settings = load_settings()
