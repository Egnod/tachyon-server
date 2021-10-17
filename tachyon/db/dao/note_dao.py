import secrets
from http import HTTPStatus
from typing import Optional, Tuple

from passlib.hash import argon2

from tachyon.db.models.note_model import NoteContentType, NoteModel
from tachyon.exceptions.dao.note import (
    NoteDAOEncryptPasswordError,
    NoteDAOException,
    NoteDAONotFound,
    NoteDAOSignError,
)
from tachyon.services.ciphers.chacha20poly1305 import ChaCha20Poly1305


class NoteDAO:
    """Class for accessing note table."""

    SIGN_LENGTH = 43
    SIGN_BYTES_LENGTH = 32

    async def create(
        self,
        name: str,
        text: str,
        content_type: NoteContentType = NoteContentType.text,
        max_number_visits: Optional[int] = None,
        is_encrypted: bool = False,
        encrypt_password: Optional[str] = None,
    ) -> str:
        """Create note.

        :param name: note name
        :param text: note content
        :param content_type: content type (only text, others - coming soon)
        :param max_number_visits: max visits for this note
        :param is_encrypted: note encryption switch-parameter
        :param encrypt_password: if is_encrypted - password for note cipher
        :return: note sign
        :raises NoteDAOException: raise for encryption data error (password is none)
        """
        note_creation_params = {
            "name": name,
            "text": text.encode(),
            "content_type": content_type,
            "max_number_visits": max_number_visits,
            "is_encrypted": is_encrypted,
            "sign": await self._generate_sign(),
        }

        note = NoteModel()
        await note.update_from_dict(note_creation_params)

        if is_encrypted:
            if not encrypt_password:
                raise NoteDAOException(
                    "Param is_encrypted for note set to true, "
                    "but encrypt_password isn't set.",
                )

            cipher = ChaCha20Poly1305(encrypt_password)

            note.encrypt_password_hash = self._password_hash(encrypt_password)
            note.text = cipher.encrypt(text)
            note.encrypt_metadata = cipher.metadata

        await note.save()

        return note_creation_params["sign"]

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

        note = await NoteModel.get_or_none(sign=sign)

        if not note:
            raise NoteDAONotFound(
                "Note not found!",
                http_code=HTTPStatus.NOT_FOUND,
            )

        message_data = note.text

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

            cipher = ChaCha20Poly1305(password, **note.encrypt_metadata)

            message_data = cipher.decrypt(message_data)

        note.current_number_visits += 1

        if note.max_number_visits is not None:
            if note.current_number_visits >= note.max_number_visits:
                await note.delete()

        await note.save()

        message_data = message_data.decode()

        return note, message_data

    @classmethod
    async def _generate_sign(cls) -> str:
        generated_sign = None

        while not generated_sign:
            sign = secrets.token_urlsafe(cls.SIGN_BYTES_LENGTH)

            if not await NoteModel.exists(sign=sign):
                generated_sign = sign

        return generated_sign

    @classmethod
    def _password_check(cls, password: str, password_hash: str) -> bool:
        return argon2.verify(password, password_hash)

    @classmethod
    def _password_hash(cls, password: str) -> str:
        return argon2.hash(password)