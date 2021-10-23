import re
import secrets
from http import HTTPStatus
from typing import Optional, Tuple

import nacl.exceptions
import nacl.pwhash
from ibmcloudant.cloudant_v1 import Document

from tachyon.db.dao.base_dao import BaseDAO
from tachyon.db.models.note_model import NoteContentType, NoteModel
from tachyon.exceptions.dao.note import (
    NoteDAOEncryptPasswordError,
    NoteDAOException,
    NoteDAONotFound,
    NoteDAOSignError,
)
from tachyon.services.ciphers.chacha20poly1305 import ChaCha20Poly1305
from tachyon.settings import settings


class NoteDAO(BaseDAO):
    """Class for accessing note table."""

    SIGN_LENGTH = 43
    SIGN_BYTES_LENGTH = 32

    _base_name = settings.notes_base

    async def create(
        self,
        name: str,
        text: str,
        content_type: NoteContentType = NoteContentType.text,
        max_number_visits: int = 0,
        is_encrypted: bool = False,
        encrypt_password: Optional[str] = None,
    ) -> str:
        """Create note.

        :param name: note name
        :param text: note content
        :param content_type: content type (only text, others - coming soon)
        :param max_number_visits: max visits for this note, min=0
        :param is_encrypted: note encryption switch-parameter
        :param encrypt_password: if is_encrypted - password for note cipher
        :return: note sign
        :raises NoteDAOException: raise for encryption data error (password is none)
        """
        note_creation_params = {
            "name": name,
            "content_type": content_type,
            "max_number_visits": max_number_visits,
            "is_encrypted": is_encrypted,
        }

        note = NoteModel(**note_creation_params)

        note.set_text(text.encode())

        if is_encrypted:
            if not encrypt_password:
                raise NoteDAOException(
                    "Param is_encrypted for note set to true, "
                    "but encrypt_password isn't set.",
                )

            cipher = ChaCha20Poly1305(encrypt_password)

            note.encrypt_password_hash = self._password_hash(encrypt_password)
            note.set_text(cipher.encrypt(text))
            note.set_encrypt_metadata(cipher.metadata)

        note = note.dict(exclude={"key"})
        note["sign"] = await self._generate_sign()

        note = Document(id=note["sign"], **note)

        self._client.put_document(db=self._base_name, doc_id=note.id, document=note)

        return note.sign

    async def read(
        self,
        sign: str,
        password: Optional[str] = None,
    ) -> Tuple[NoteModel, str]:
        """Create note.

        :param sign: note sign
        :param password: password for note cipher
        :return: note and message
        :raises NoteDAONotFound: if note not found by sign
        :raises NoteDAOEncryptPasswordError: if password is wrong or no password
        :raises NoteDAOSignError: if received sign not allowed by conditions
        """
        if len(sign) != self.SIGN_LENGTH:
            raise NoteDAOSignError(
                "Sign must be 32 characters long",
                http_code=HTTPStatus.BAD_REQUEST,
            )

        note = next(
            iter(
                (self._client.post_find(self._base_name, {"sign": sign})).get_result()[
                    "docs"
                ],
            ),
            None,
        )  # : WPS221

        if not note:
            raise NoteDAONotFound(
                message="Note not found!",
                http_code=HTTPStatus.NOT_FOUND,
            )

        note = NoteModel(**note)

        if note.is_encrypted:
            if not password:
                raise NoteDAOEncryptPasswordError(
                    "This note encrypted, but password is none!",
                    http_code=HTTPStatus.BAD_REQUEST,
                )

            if not self._password_check(password, note.encrypt_password_hash):
                raise NoteDAOEncryptPasswordError(
                    "This note encrypted, but password is wrong!",
                    http_code=HTTPStatus.BAD_REQUEST,
                )

            cipher = ChaCha20Poly1305(password, **note.get_encrypt_metadata())

            message_data = cipher.decrypt(note.get_text(decode=False)).decode()

        else:
            message_data = note.get_text()

        note.current_number_visits += 1

        updated_note = note.dict(by_alias=True)

        updated_note = self._client.post_document(
            db=self._base_name,
            document=updated_note,
        ).get_result()

        if note.max_number_visits:
            if note.current_number_visits >= note.max_number_visits:
                self._client.delete_document(
                    db=self._base_name,
                    doc_id=updated_note["id"],
                    rev=updated_note["rev"],
                )

        return note, message_data

    async def _generate_sign(self) -> str:
        generated_sign = None

        while not generated_sign:
            sign = secrets.token_urlsafe(self.SIGN_BYTES_LENGTH)

            if (
                re.match("^[^_].*", sign)
                and not self._client.post_find(
                    db=self._base_name,
                    selector={"sign": {"$eq": sign}},
                    fields=["_id"],
                    limit=1,
                ).get_result()["docs"]
            ):
                generated_sign = sign

        return generated_sign

    @classmethod
    def _password_check(cls, password: str, password_hash: str) -> bool:
        try:
            return nacl.pwhash.verify(password_hash.encode(), password.encode())
        except nacl.exceptions.InvalidkeyError:
            return False

    @classmethod
    def _password_hash(cls, password: str) -> str:
        return nacl.pwhash.str(password.encode()).decode()
