import logging
from typing import Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from ibm_cloud_sdk_core import ApiException
from starlette.requests import Request
from starlette.responses import JSONResponse

from tachyon.exceptions.base import BaseTachyonException

logger = logging.getLogger("web_exception")


async def tachyon_exception_handler(
    request: Request,
    exc: Union[BaseTachyonException, ApiException],
) -> JSONResponse:
    """Handler for transmit internal tachyon exception to HTTP.

    :param request: current request data
    :param exc: tachyon exception data
    :returns: response data
    """
    logger.exception(exc)

    return JSONResponse(
        content=jsonable_encoder({"detail": exc.message}),
        status_code=exc.code,
    )


exception_handlers = {
    BaseTachyonException: tachyon_exception_handler,
    ApiException: tachyon_exception_handler,
}


def add_exception_handlers(app: FastAPI) -> None:
    """Connect handlers from exception_handlers.

    :param app: app for connect handlers
    """
    for exception, exception_handler in exception_handlers.items():
        app.add_exception_handler(exception, exception_handler)
