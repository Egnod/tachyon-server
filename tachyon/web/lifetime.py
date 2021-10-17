from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import RedisCacheBackend

from tachyon.settings import settings


def startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application startup.

    This function use fastAPI app to store data,
    such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    async def _startup() -> None:  # noqa: WPS430
        rc = RedisCacheBackend(settings.redis_uri)
        caches.set(settings.redis_key, rc)

    return _startup


def shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    async def _shutdown() -> None:  # noqa: WPS430
        await close_caches()

    return _shutdown
