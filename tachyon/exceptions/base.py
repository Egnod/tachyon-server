from http import HTTPStatus
from typing import Any, Dict, Optional


class BaseTachyonException(Exception):
    """Base exception class for internal errors."""

    def __init__(
        self,
        message: Optional[str] = None,
        http_code: int = HTTPStatus.OK,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.http_code = http_code
        self.message = message.format(params or {}) if message else None

    def __str__(self) -> str:
        return self.message or str(self)
