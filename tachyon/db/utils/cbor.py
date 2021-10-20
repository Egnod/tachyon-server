import base64
from typing import Any, Union

import cbor2


def dumps(data: Any) -> str:
    """Encode data to cbor and encode this to b85 (base65 function).

    :param data: data for encoding
    :return: base64 string
    """
    return base64.b85encode(cbor2.dumps(data)).decode()


def loads(data: Union[str, bytes]) -> Any:
    """Decode data from string b85 (base65 function) and decode cbor to data.

    :param data: data for decoding
    :return: base64 string
    """
    return cbor2.loads(base64.b85decode(data))
