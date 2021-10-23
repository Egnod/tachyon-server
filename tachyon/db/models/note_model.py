import base64
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from tachyon.db.utils import cbor


class NoteContentType(str, Enum):  # noqa: WPS600
    """Enum of note content types."""

    text = "text"


class NoteModel(BaseModel):
    """Model for notes purpose."""

    key: Optional[str] = Field(default=None, alias="_id")

    sign: Optional[str] = Field(default=None)

    name: str = Field(...)
    content_type: NoteContentType = Field(default=NoteContentType.text)

    max_number_visits: int = Field(default=0, ge=0)
    current_number_visits: int = Field(default=0, ge=0)

    is_encrypted: bool = Field(default=False)
    encrypt_password_hash: Optional[str] = Field(default=None)

    encrypt_metadata: Optional[str] = Field(default=None)

    text: str = Field(default="")

    def get_text(self, decode: bool = True) -> Union[str, bytes]:
        """Text from b85 format.

        :param decode: decode to utf-8 or not
        :return: text
        """
        return (
            base64.b85decode(self.text).decode()
            if decode
            else base64.b85decode(self.text)
        )

    def set_text(self, value: bytes) -> None:
        """Text to b85 format.

        :param value: text for b85 encode
        """
        self.text = base64.b85encode(value).decode()  # noqa: WPS601

    def get_encrypt_metadata(self) -> Dict[str, Any]:
        """Encryption data from cbor format.

        :return: dict of metadata
        """
        return cbor.loads(self.encrypt_metadata)

    def set_encrypt_metadata(self, value: Any) -> None:
        """Encryption data to cbor format.

        :param value: encryption metadata for cbor encode
        """
        self.encrypt_metadata = cbor.dumps(value)  # noqa: WPS601

    class Config:
        allow_population_by_field_name = True
        extra = "allow"
