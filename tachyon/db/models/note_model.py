from enum import Enum
from typing import Any, Dict

from tortoise import fields, models

from tachyon.db.utils import cbor


class NoteContentType(str, Enum):  # noqa: WPS600
    """Enum of note content types."""

    text = "text"


class NoteModel(models.Model):
    """Model for notes purpose."""

    id = fields.IntField(pk=True)
    sign = fields.CharField(max_length=255, unique=True)  # noqa: WPS432

    name = fields.CharField(max_length=200)  # noqa: WPS432
    content_type = fields.CharEnumField(NoteContentType, max_length=200)  # noqa: WPS432

    max_number_visits = fields.IntField(default=None, null=True)
    current_number_visits = fields.IntField(default=0)  # : WPS432

    is_encrypted = fields.BooleanField(default=False)
    encrypt_password_hash = fields.TextField(default=None, null=True)
    _encrypt_metadata = fields.BinaryField(
        source_field="encrypt_metadata",
        null=True,
        default=None,
    )

    text = fields.BinaryField()

    @property
    def encrypt_metadata(self) -> Dict[str, Any]:
        """Encryption data from cbor format.

        :return: dict of metadata
        """
        return cbor.loads(self._encrypt_metadata)

    @encrypt_metadata.setter
    def encrypt_metadata(self, value: Any) -> None:
        """Encryption data to cbor format.

        :param value: encryption metadata for cbor encode
        """
        self._encrypt_metadata = cbor.dumps(value)  # noqa: WPS601

    def __str__(self) -> str:
        return self.name
