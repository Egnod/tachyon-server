from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from tachyon import __version__
from tachyon.db.config import TORTOISE_CONFIG
from tachyon.web.api import root
from tachyon.web.api.router import api_router
from tachyon.web.exceptions import add_exception_handlers
from tachyon.web.lifetime import shutdown, startup

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="tachyon",
        description="Crypto notes with many settings and templates!",
        version=__version__,
        docs_url="/api/docs/",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.on_event("startup")(startup(app))
    app.on_event("shutdown")(shutdown(app))

    add_exception_handlers(app)

    app.include_router(router=api_router, prefix="/api")
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )
    app.include_router(router=root.router)

    register_tortoise(app, config=TORTOISE_CONFIG, add_exception_handlers=True)

    return app
