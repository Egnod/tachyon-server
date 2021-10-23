import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from tachyon.settings import settings


def sentry_init() -> None:
    """Add sentry middleware to app if dsn exists."""
    if settings.sentry_dsn:
        LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )
        sentry_sdk.init(settings.sentry_dsn, environment=settings.sentry_env)
