from typing import Optional

from fastapi import APIRouter
from fastapi.param_functions import Depends, Path, Query

from tachyon.db.dao.note_dao import NoteDAO
from tachyon.web.api.note.schemas import (
    NoteCreateRequest,
    NoteCreateResponse,
    NoteReadResponse,
)

router = APIRouter()


@router.get("/{sign}", response_model=NoteReadResponse)
async def read_note(
    sign: str = Path(...),
    password: Optional[str] = Query(default=None),
    note_dao: NoteDAO = Depends(),
) -> NoteReadResponse:
    """
    Read note message in database.

    :param password: password for read note.
    :param note_dao: DAO for note models.
    :param sign: unique identity for note find.

    :returns: note read message
    """
    note, message = await note_dao.read(sign, password=password)

    return NoteReadResponse(message=message, name=note.name)


@router.post("/", response_model=NoteCreateResponse)
async def create_note(
    schema: NoteCreateRequest,
    note_dao: NoteDAO = Depends(),
) -> NoteCreateResponse:
    """
    Read note message in database.

    :param schema: params for create note.
    :param note_dao: DAO for note models.

    :returns: note sing
    """
    return NoteCreateResponse(
        sign=await note_dao.create(
            name=schema.name,
            text=schema.text,
            content_type=schema.content_type,
            max_number_visits=schema.max_number_visits,
            is_encrypted=schema.is_encrypted,
            encrypt_password=schema.encrypt_password,
        ),
    )
