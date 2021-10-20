from pydantic import BaseModel


class StatResponse(BaseModel):
    """Response schema for stat."""

    current_notes_count: int
