from fastapi import APIRouter

from tachyon.web.api.monitoring.schemas import StatResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """


@router.get("/stat", response_model=StatResponse)
async def simple_stat() -> StatResponse:
    """
    Simple stats of notes.

    It returns 200 if the project is healthy.
    :return: simple notes stat
    """
    return StatResponse(
        current_notes_count=0,
    )
