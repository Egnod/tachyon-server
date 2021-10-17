from pathlib import Path
from tempfile import gettempdir

from fastapi_cache.backends.redis import CACHE_KEY
from pydantic import BaseSettings, Field
from yarl import URL

TEMP_DIR = Path(gettempdir())


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "tachyon"
    db_pass: str = "tachyon"
    db_base: str = "tachyon"
    db_echo: bool = False

    redis_key: str = CACHE_KEY
    redis_uri: str = Field(...)

    server_crypto_secret: str = Field(...)

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgres",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

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
