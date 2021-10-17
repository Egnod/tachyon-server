import uuid
from random import randint

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from tachyon.db.dao.note_dao import NoteDAO
from tachyon.db.models.note_model import NoteContentType
from tachyon.exceptions.dao.note import (
    NoteDAOEncryptPasswordError,
    NoteDAONotFound,
    NoteDAOSignError,
)


@pytest.mark.asyncio
async def test_we_creation(
    fastapi_app: FastAPI,
    client: TestClient,
) -> None:
    """Tests note instance creation (without encryption)."""
    url = fastapi_app.url_path_for("create_note")
    test_name = uuid.uuid4().hex
    test_max_number_visits = 1
    test_text = uuid.uuid4().hex

    response = client.post(
        url,
        json={
            "name": test_name,
            "content_type": "text",
            "max_number_visits": test_max_number_visits,
            "text": test_text,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    sign = response.json()["sign"]

    dao = NoteDAO()
    instance, message = await dao.read(sign=sign)

    assert instance.name == test_name
    assert instance.max_number_visits == test_max_number_visits
    assert instance.text == test_text.encode() == message.encode()

    with pytest.raises(NoteDAONotFound):
        await dao.read(sign=sign)

    with pytest.raises(NoteDAOSignError):
        await dao.read(sign="123")

    # Without max visits limit

    response = client.post(
        url,
        json={
            "name": test_name,
            "content_type": "text",
            "text": test_text,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    sign = response.json()["sign"]

    dao = NoteDAO()
    instance, message = await dao.read(sign=sign)

    assert instance.name == test_name
    assert instance.max_number_visits is None
    assert instance.text == test_text.encode() == message.encode()

    with pytest.raises(NoteDAOSignError):
        await dao.read(sign="123")

    for _ in range(randint(5, 25)):
        await dao.read(sign=sign)


@pytest.mark.asyncio
async def test_creation(
    fastapi_app: FastAPI,
    client: TestClient,
) -> None:
    """Tests note instance creation (with encryption)."""
    url = fastapi_app.url_path_for("create_note")
    test_name = uuid.uuid4().hex
    test_text = uuid.uuid4().hex
    test_encrypt_password = uuid.uuid4().hex
    test_wrong_encrypt_password = uuid.uuid4().hex

    # with password and is_encrypted=false

    response = client.post(
        url,
        json={
            "name": test_name,
            "content_type": "text",
            "text": test_text,
            "encrypt_password": test_encrypt_password,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    sign = response.json()["sign"]

    dao = NoteDAO()
    instance, message = await dao.read(sign=sign)

    assert instance.name == test_name
    assert instance.text == test_text.encode() == message.encode()
    assert instance.encrypt_password_hash is None

    # with password and is_encrypted=true

    response = client.post(
        url,
        json={
            "name": test_name,
            "content_type": "text",
            "text": test_text,
            "encrypt_password": test_encrypt_password,
            "is_encrypted": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    sign = response.json()["sign"]

    dao = NoteDAO()
    instance, message = await dao.read(sign=sign, password=test_encrypt_password)

    assert instance.name == test_name
    assert instance.text != test_text.encode()
    assert instance.encrypt_password_hash is not None
    assert test_text == message

    with pytest.raises(NoteDAOEncryptPasswordError):
        await dao.read(sign=sign)

    with pytest.raises(NoteDAOEncryptPasswordError):
        await dao.read(sign=sign, password=test_wrong_encrypt_password)


@pytest.mark.asyncio
async def test_read(
    fastapi_app: FastAPI,
    client: TestClient,
) -> None:
    """Tests note instance read (without encryption)."""
    test_name = uuid.uuid4().hex
    test_max_number_visits = 1
    test_text = uuid.uuid4().hex

    dao = NoteDAO()

    sign = await dao.create(
        name=test_name,
        text=test_text,
        content_type=NoteContentType.text,
        is_encrypted=False,
        max_number_visits=test_max_number_visits,
    )

    url = fastapi_app.url_path_for("read_note", sign=sign)

    response = client.get(
        url,
        json={},
    )

    assert response.status_code == status.HTTP_200_OK

    note_data = response.json()

    assert note_data["name"] == test_name
    assert note_data["message"] == test_text

    response = client.get(
        url,
        json={},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Without max visits limit

    sign = await dao.create(
        name=test_name,
        text=test_text,
        content_type=NoteContentType.text,
        is_encrypted=False,
    )

    url = fastapi_app.url_path_for("read_note", sign=sign)

    response = client.get(
        url,
        json={},
    )

    assert response.status_code == status.HTTP_200_OK

    note_data = response.json()

    assert note_data["name"] == test_name
    assert note_data["message"] == test_text

    response = client.get(
        url,
        json={},
    )

    assert response.status_code == status.HTTP_200_OK
