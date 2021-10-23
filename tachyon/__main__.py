import uvicorn

from tachyon.settings import settings
from tachyon.web.application import get_app

app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "tachyon.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        factory=True,
    )
