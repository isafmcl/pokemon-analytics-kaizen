from __future__ import annotations
from functools import lru_cache
from typing import Literal
import os
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseModel, field_validator


class Settings(BaseModel):
    api_base_url: AnyHttpUrl
    api_username: str
    api_password: str
    database_url: str
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    request_timeout_seconds: float = 10.0
    max_retries: int = 3
    page_size_default: int = 100

    @field_validator("api_base_url", mode="before")
    @classmethod
    def _strip_trailing_slash(cls, value: str | AnyHttpUrl) -> str:
        url_str = str(value)
        return url_str.rstrip("/")


def _load_env_file(env_file: str | None = None) -> None:

    load_dotenv(dotenv_path=env_file, override=False)


@lru_cache(maxsize=1)
def get_settings(env_file: str | None = None) -> Settings:

    _load_env_file(env_file)

    api_base_url = os.environ["API_BASE_URL"]
    api_username = os.environ["API_USERNAME"]
    api_password = os.environ["API_PASSWORD"]
    database_url = os.environ["DATABASE_URL"]

    log_level_env = os.environ.get("LOG_LEVEL", "INFO").upper()
    request_timeout_env = os.environ.get("REQUEST_TIMEOUT_SECONDS", "10")
    max_retries_env = os.environ.get("MAX_RETRIES", "3")
    page_size_env = os.environ.get("PAGE_SIZE_DEFAULT", "100")

    return Settings(
        api_base_url=api_base_url,
        api_username=api_username,
        api_password=api_password,
        database_url=database_url,
        log_level=log_level_env,
        request_timeout_seconds=float(request_timeout_env),
        max_retries=int(max_retries_env),
        page_size_default=int(page_size_env),
    )
