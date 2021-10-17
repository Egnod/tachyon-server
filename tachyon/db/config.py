from typing import List

from tachyon.settings import settings

MODELS_MODULES: List[str] = ["tachyon.db.models.note_model"]  # noqa: WPS407

TORTOISE_CONFIG = {  # noqa: WPS407
    "connections": {
        "default": str(settings.db_url),
    },
    "apps": {
        "models": {
            "models": ["aerich.models"] + MODELS_MODULES,
            "default_connection": "default",
        },
    },
}
