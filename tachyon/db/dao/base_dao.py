from abc import ABC
from http import HTTPStatus
from typing import Optional

from ibm_cloud_sdk_core import ApiException
from ibmcloudant import CloudantV1

from tachyon.settings import settings


class BaseDAO(ABC):
    """Base abstract-class for DAO."""

    _base_name: str = ""
    _client_instance: Optional[CloudantV1] = None

    @staticmethod
    def _create_client() -> CloudantV1:
        """Create new cloudant client to service.

        :return: cloudant client
        """
        return CloudantV1.new_instance(settings.cloudant_service_name)

    def _delete_db(self) -> None:
        self._client.delete_database(self._base_name)

    def _populate_db(self) -> None:
        try:
            self._client.put_database(self._base_name)
        except ApiException as exc:
            if exc.code != HTTPStatus.PRECONDITION_FAILED:
                raise

    @property
    def _client(self) -> CloudantV1:
        """Get or create cloudant client property.

        :return: cloudant client
        """
        if not self._client_instance:
            self._client_instance = self._create_client()  # noqa: WPS601

            self._populate_db()

        return self._client_instance
