import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from tachyon.settings import settings


def sentry_init(app: FastAPI) -> None:
    """Add sentry middleware to app if dsn exists.

    :param app: fastapi app
    """
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn)

        app.add_middleware(SentryAsgiMiddleware)
