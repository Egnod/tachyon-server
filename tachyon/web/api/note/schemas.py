from typing import Optional

from pydantic import BaseModel, Field

from tachyon.db.models.note_model import NoteContentType


class NoteReadResponse(BaseModel):
    """Response schema for read note message."""

    name: str
    message: str


class NoteCreateRequest(BaseModel):
    """Request schema for create note."""

    name: str = Field(...)
    content_type: NoteContentType = Field(default=NoteContentType.text)
    max_number_visits: int = Field(default=0, ge=0)
    is_encrypted: bool = Field(default=False)
    encrypt_password: Optional[str] = Field(default=None)
    text: str = Field(...)


class NoteCreateResponse(BaseModel):
    """Response schema for create note."""

    sign: str = Field(...)
