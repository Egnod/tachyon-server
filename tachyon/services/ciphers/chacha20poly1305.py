import base64
import os
from hashlib import sha3_256
from typing import Dict, Optional, Union

from cryptography.hazmat.primitives.ciphers import aead

from tachyon.settings import settings


class ChaCha20Poly1305:
    """Interface for chacha20-poly1305."""

    NONCE_LENGTH = 12

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

        self._key = key or sha3_256(password.encode()).digest()
        self._nonce = nonce or os.urandom(self.NONCE_LENGTH)
        self._aad = aad or settings.crypto_secret

        self._algorithm = aead.ChaCha20Poly1305(self._key)

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

        return self._algorithm.encrypt(self._nonce, message_data, self._aad)

    def decrypt(self, message_data: Union[str, bytes]) -> bytes:
        """Decrypt string or bytes data.

        :param message_data: string or bytes data for decrypt
        :returns: bytes decrypted message
        """
        if isinstance(message_data, str):
            message_data = message_data.encode()

        return self._algorithm.decrypt(self._nonce, message_data, self._aad)
