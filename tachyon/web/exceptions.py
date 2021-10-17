from typing import Type

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse

from tachyon.exceptions.base import BaseTachyonException


async def tachyon_exception_handler(
    request: Request,
    exc: Type[BaseTachyonException],
) -> JSONResponse:
    """Handler for transmit internal tachyon exception to HTTP.

    :param request: current request data
    :param exc: tachyon exception data
    :returns: response data
    """
    return JSONResponse(
        content=jsonable_encoder({"detail": exc.message}),
        status_code=exc.http_code,
    )


exception_handlers = {
    BaseTachyonException: tachyon_exception_handler,
}


def add_exception_handlers(app: FastAPI) -> None:
    """Connect handlers from exception_handlers.

    :param app: app for connect handlers
    """
    for exception, exception_handler in exception_handlers.items():
        app.add_exception_handler(exception, exception_handler)
