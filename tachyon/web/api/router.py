from fastapi.routing import APIRouter

from tachyon.web.api import monitoring, note

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(note.router, prefix="/note", tags=["note"])
