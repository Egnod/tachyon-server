from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from fastapi_cache.backends.redis import CACHE_KEY
from pydantic import BaseSettings, Field

TEMP_DIR = Path(gettempdir())


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False
    db_url: str = "postgres://tachyon:tachyon@localhost:5432/tachyon"
    db_echo: bool = False

    redis_key: str = CACHE_KEY
    redis_uri: str = Field(default="redis://tachyon-redis:6379")

    server_crypto_secret: str = Field(default="super_secret")

    sentry_dsn: Optional[str] = None

    @property
    def crypto_secret(self) -> bytes:
        """Crypto secret as bytes.

        :returns: bytes of crypto secret
        """
        return self.server_crypto_secret.encode()

    class Config:
        env_file = ".env"
        env_prefix = "TACHYON_"
        env_file_encoding = "utf-8"


settings = Settings()
