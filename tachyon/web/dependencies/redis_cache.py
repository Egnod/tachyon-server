from typing import Any

from fastapi_cache import caches

from tachyon.settings import settings


def redis_cache() -> Any:
    """Read fastapi-cache from redis.

    :return: cache from redis
    """
    return caches.get(settings.redis_key)
