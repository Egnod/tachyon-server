from pydantic import BaseModel


class RootCheckResponse(BaseModel):
    """Response schema for root check."""

    version: str
    root_crypto_secret_hash: str
