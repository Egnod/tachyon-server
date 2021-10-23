import base64
import secrets
from hashlib import shake_256
from typing import Dict, Optional, Union

from Cryptodome.Cipher import ChaCha20_Poly1305

from tachyon.settings import settings


class ChaCha20Poly1305:
    """Interface for chacha20-poly1305."""

    NONCE_LENGTH = 12
    KEY_LENGTH = 32

    def __init__(
        self,
        password: str,
        key: Optional[Union[bytes, str]] = None,
        nonce: Optional[Union[bytes, str]] = None,
        aad: Optional[Union[bytes, str]] = None,
    ):
        if isinstance(key, str):
            key = base64.b85decode(key)

        if isinstance(nonce, str):
            nonce = base64.b85decode(nonce)

        if isinstance(aad, str):
            aad = base64.b85decode(aad)

        self._key = key or shake_256(password.encode()).digest(self.KEY_LENGTH)
        self._nonce = nonce or secrets.token_bytes(self.NONCE_LENGTH)
        self._aad = aad or settings.crypto_secret

        self._algorithm = ChaCha20_Poly1305.new(key=self._key, nonce=self._nonce)
        self._algorithm.update(self._aad)

    @property
    def metadata(self) -> Dict[str, str]:
        """Encryption additional data (nonce, etc.).

        :returns: nonce for decrypt
        """
        return {
            "nonce": base64.b85encode(self._nonce).decode(),
        }

    def encrypt(self, message_data: Union[str, bytes]) -> bytes:
        """Encrypt string or bytes data.

        :param message_data: string or bytes data for encrypt
        :returns: bytes encrypted message
        """
        if isinstance(message_data, str):
            message_data = message_data.encode()

        return self._algorithm.encrypt(message_data)

    def decrypt(self, message_data: Union[str, bytes]) -> bytes:
        """Decrypt string or bytes data.

        :param message_data: string or bytes data for decrypt
        :returns: bytes decrypted message
        """
        if isinstance(message_data, str):
            message_data = message_data.encode()

        return self._algorithm.decrypt(message_data)
