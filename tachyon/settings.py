from pathlib import Path
from tempfile import gettempdir
from typing import Optional

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

    deta_key: str = Field(...)

    server_crypto_secret: str = Field(default="super_secret")

    notes_base: str = Field(default="notes")

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
