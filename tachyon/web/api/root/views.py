from hashlib import sha3_512

from fastapi import APIRouter

from tachyon import __version__
from tachyon.settings import settings
from tachyon.web.api.root.schemas import RootCheckResponse

router = APIRouter()


@router.get("/", response_model=RootCheckResponse)
def root_check() -> RootCheckResponse:
    """
    Checks the root info of a project.

    It returns version and root_crypto_secret_hash.

    :return: RootCheckResponse
    """
    return RootCheckResponse(
        version=__version__,
        root_crypto_secret_hash=sha3_512(settings.crypto_secret).hexdigest(),
    )
